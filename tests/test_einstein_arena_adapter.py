#!/usr/bin/env python3
"""Unit tests for scripts/einstein_arena_adapter.py."""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import einstein_arena_adapter as adapter  # type: ignore


class EinsteinArenaAdapterTests(unittest.TestCase):
    def test_verify_pow_and_solve_pow_roundtrip(self) -> None:
        challenge = "omega-test"
        difficulty = 8
        nonce = adapter.solve_pow(challenge, difficulty, max_nonce=2_000_000)
        self.assertTrue(adapter.verify_pow(challenge, difficulty, nonce))
        self.assertFalse(adapter.verify_pow(challenge, difficulty, max(0, nonce - 1)))

    def test_solve_pow_respects_timeout(self) -> None:
        with patch.object(adapter, "verify_pow", return_value=False):
            with self.assertRaisesRegex(RuntimeError, "PoW timed out"):
                adapter.solve_pow("omega-timeout", difficulty=24, max_nonce=500_000, max_seconds=0.0)

    def test_parse_solution_payload_inline_json(self) -> None:
        payload = adapter.parse_solution_payload('{"values": [0.5, 0.25]}', None)
        self.assertEqual(payload["values"], [0.5, 0.25])

    def test_parse_solution_payload_json_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            solution_path = Path(tmpdir) / "solution.json"
            solution_path.write_text('{"coeffs": [1, -1, 1]}', encoding="utf-8")
            payload = adapter.parse_solution_payload(None, str(solution_path))
        self.assertEqual(payload["coeffs"], [1, -1, 1])

    def test_parse_solution_payload_rejects_invalid_argument_combinations(self) -> None:
        with self.assertRaises(ValueError):
            adapter.parse_solution_payload('{"x": 1}', "solution.json")

        with self.assertRaises(ValueError):
            adapter.parse_solution_payload(None, None)

    def test_register_agent_happy_path(self) -> None:
        with patch.object(adapter, "request_json") as mocked_request, patch.object(adapter, "solve_pow") as mocked_pow:
            mocked_request.side_effect = [
                {"challenge": "challenge-token", "difficulty": 12},
                {"agent": {"name": "OmegaAgent", "api_key": "ea_test_key"}},
            ]
            mocked_pow.return_value = 4242

            result = adapter.register_agent("https://einsteinarena.com", "OmegaAgent")

        self.assertEqual(result["name"], "OmegaAgent")
        self.assertEqual(result["api_key"], "ea_test_key")
        self.assertEqual(result["difficulty"], 12)
        self.assertEqual(result["nonce"], 4242)

    def test_register_agent_rejects_malformed_payloads(self) -> None:
        with patch.object(adapter, "request_json", return_value="not-a-dict"):
            with self.assertRaisesRegex(RuntimeError, "Challenge response is not a JSON object"):
                adapter.register_agent("https://einsteinarena.com", "OmegaAgent")

        with patch.object(adapter, "request_json") as mocked_request, patch.object(adapter, "solve_pow", return_value=1):
            mocked_request.side_effect = [
                {"challenge": "challenge-token", "difficulty": 12},
                {"agent": {"name": "OmegaAgent"}},
            ]
            with self.assertRaisesRegex(RuntimeError, "missing agent.api_key"):
                adapter.register_agent("https://einsteinarena.com", "OmegaAgent")

    def test_request_json_surfaces_http_error_message(self) -> None:
        err = urllib.error.HTTPError(
            url="https://einsteinarena.com/api/problems",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":"invalid payload"}'),
        )

        with patch("urllib.request.urlopen", side_effect=err):
            with self.assertRaisesRegex(RuntimeError, "HTTP 400 on /api/problems: invalid payload"):
                adapter.request_json("GET", "https://einsteinarena.com", "/api/problems")

    def test_request_json_surfaces_network_error_message(self) -> None:
        err = urllib.error.URLError("dns failure")
        with patch("urllib.request.urlopen", side_effect=err):
            with self.assertRaisesRegex(RuntimeError, "Network error on /api/problems: dns failure"):
                adapter.request_json("GET", "https://einsteinarena.com", "/api/problems")

    def test_request_json_sets_auth_header_and_timeout(self) -> None:
        class _FakeResponse:
            def __init__(self, payload: bytes) -> None:
                self._payload = payload

            def __enter__(self) -> "_FakeResponse":
                return self

            def __exit__(self, exc_type, exc, tb) -> bool:
                return False

            def read(self) -> bytes:
                return self._payload

        with patch("urllib.request.urlopen", return_value=_FakeResponse(b"{}")) as mocked_open:
            result = adapter.request_json(
                "POST",
                "https://einsteinarena.com",
                "/api/solutions",
                payload={"problem_id": 1},
                api_key="ea_token",
                timeout_seconds=12,
            )

        self.assertEqual(result, {})
        request_obj = mocked_open.call_args.args[0]
        timeout_value = mocked_open.call_args.kwargs.get("timeout")
        self.assertEqual(timeout_value, 12)
        self.assertEqual(request_obj.headers.get("Authorization"), "Bearer ea_token")
        self.assertEqual(request_obj.headers.get("Content-type"), "application/json")

    def test_request_json_retries_retryable_http_error_then_succeeds(self) -> None:
        class _FakeResponse:
            def __init__(self, payload: bytes) -> None:
                self._payload = payload

            def __enter__(self) -> "_FakeResponse":
                return self

            def __exit__(self, exc_type, exc, tb) -> bool:
                return False

            def read(self) -> bytes:
                return self._payload

        transient = urllib.error.HTTPError(
            url="https://einsteinarena.com/api/problems",
            code=503,
            msg="Service Unavailable",
            hdrs=None,
            fp=io.BytesIO(b'{"error":"temporarily unavailable"}'),
        )

        with patch("urllib.request.urlopen", side_effect=[transient, _FakeResponse(b'{"ok": true}')]), patch(
            "time.sleep"
        ) as mocked_sleep:
            result = adapter.request_json(
                "GET",
                "https://einsteinarena.com",
                "/api/problems",
                max_retries=2,
                retry_backoff_seconds=0.1,
            )

        self.assertEqual(result, {"ok": True})
        mocked_sleep.assert_called_once_with(0.1)

    def test_request_json_retries_timeout_url_error_then_succeeds(self) -> None:
        class _FakeResponse:
            def __init__(self, payload: bytes) -> None:
                self._payload = payload

            def __enter__(self) -> "_FakeResponse":
                return self

            def __exit__(self, exc_type, exc, tb) -> bool:
                return False

            def read(self) -> bytes:
                return self._payload

        timeout_err = urllib.error.URLError(TimeoutError("timed out"))
        with patch("urllib.request.urlopen", side_effect=[timeout_err, _FakeResponse(b"{}")]), patch("time.sleep") as mocked_sleep:
            result = adapter.request_json(
                "GET",
                "https://einsteinarena.com",
                "/api/problems",
                max_retries=1,
                retry_backoff_seconds=0.2,
            )

        self.assertEqual(result, {})
        mocked_sleep.assert_called_once_with(0.2)

    def test_main_submit_forwards_timeout(self) -> None:
        with patch.object(adapter, "request_json", return_value={"ok": True}) as mocked_request:
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = adapter.main(
                    [
                        "--timeout",
                        "19",
                        "--max-retries",
                        "4",
                        "--retry-backoff",
                        "0.4",
                        "submit",
                        "--api-key",
                        "ea_key",
                        "--problem-id",
                        "5",
                        "--solution-json",
                        '{"weights": [1, 2]}',
                    ]
                )

        self.assertEqual(exit_code, 0)
        self.assertTrue(mocked_request.called)
        _, kwargs = mocked_request.call_args
        self.assertEqual(kwargs.get("timeout_seconds"), 19)
        self.assertEqual(kwargs.get("max_retries"), 4)
        self.assertEqual(kwargs.get("retry_backoff_seconds"), 0.4)
        self.assertEqual(kwargs.get("api_key"), "ea_key")

    def test_main_register_forwards_retry_controls(self) -> None:
        with patch.object(adapter, "register_agent", return_value={"name": "OmegaAgent", "api_key": "ea_key"}) as mocked_register:
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = adapter.main(
                    [
                        "--timeout",
                        "11",
                        "--max-retries",
                        "6",
                        "--retry-backoff",
                        "0.25",
                        "--pow-timeout",
                        "7",
                        "--pow-progress-interval",
                        "250000",
                        "register",
                        "--name",
                        "OmegaAgent",
                    ]
                )

        self.assertEqual(exit_code, 0)
        _, kwargs = mocked_register.call_args
        self.assertEqual(kwargs.get("timeout_seconds"), 11)
        self.assertEqual(kwargs.get("max_retries"), 6)
        self.assertEqual(kwargs.get("retry_backoff_seconds"), 0.25)
        self.assertEqual(kwargs.get("pow_timeout_seconds"), 7)
        self.assertEqual(kwargs.get("pow_progress_interval"), 250000)

    def test_main_threads_and_activity_forward_timeout(self) -> None:
        with patch.object(adapter, "request_json", return_value={"ok": True}) as mocked_request:
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code_threads = adapter.main(
                    [
                        "--timeout",
                        "17",
                        "threads",
                        "--slug",
                        "erdos-minimum-overlap",
                    ]
                )
            self.assertEqual(exit_code_threads, 0)
            _, kwargs_threads = mocked_request.call_args
            self.assertEqual(kwargs_threads.get("timeout_seconds"), 17)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code_activity = adapter.main(
                    [
                        "--timeout",
                        "23",
                        "activity",
                        "--api-key",
                        "ea_key",
                    ]
                )
            self.assertEqual(exit_code_activity, 0)
            _, kwargs_activity = mocked_request.call_args
            self.assertEqual(kwargs_activity.get("timeout_seconds"), 23)

    def test_main_vote_forwards_timeout_and_endpoint(self) -> None:
        with patch.object(adapter, "request_json", return_value={"ok": True}) as mocked_request:
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = adapter.main(
                    [
                        "--timeout",
                        "29",
                        "vote",
                        "--api-key",
                        "ea_key",
                        "--thread-id",
                        "15",
                        "--direction",
                        "up",
                    ]
                )

        self.assertEqual(exit_code, 0)
        call_args = mocked_request.call_args
        self.assertEqual(call_args.args[2], "/api/threads/15/upvote")
        self.assertEqual(call_args.kwargs.get("api_key"), "ea_key")
        self.assertEqual(call_args.kwargs.get("timeout_seconds"), 29)


if __name__ == "__main__":
    unittest.main()
