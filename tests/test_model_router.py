"""Tests for model_router.py — LLM backend routing, profiles, and health checks."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure scripts/ is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from model_router import (
    BACKENDS,
    PROFILES,
    Backend,
    ModelProfile,
    _infer_backend,
    check_all_backends,
    check_backend_health,
    resolve_profile,
    resolve_with_fallback,
)


# ──────────────────────────── Backend Registry ────────────────────────────────


class TestBackendRegistry:
    def test_all_expected_backends_registered(self):
        expected = {"openai", "deepseek", "anthropic", "ollama", "vllm", "lmstudio"}
        assert set(BACKENDS.keys()) == expected

    def test_each_backend_has_required_fields(self):
        for name, b in BACKENDS.items():
            assert b.name == name
            assert isinstance(b.base_url, str) and b.base_url.startswith("http")
            assert isinstance(b.api_key_env, str)
            assert isinstance(b.models, list)

    def test_local_backends_always_configured(self):
        for name in ("ollama", "vllm", "lmstudio"):
            assert BACKENDS[name].is_configured is True

    def test_remote_backends_require_api_key(self):
        for name in ("openai", "deepseek", "anthropic"):
            with patch.dict(os.environ, {BACKENDS[name].api_key_env: ""}, clear=False):
                # Force re-read: api_key is a property
                result = BACKENDS[name].api_key
                # With empty key, is_configured should be False
                assert BACKENDS[name].is_configured is False or result != ""


# ──────────────────────────── Model Profiles ──────────────────────────────────


class TestModelProfiles:
    def test_all_seven_roles_have_profiles(self):
        expected_roles = {"planner", "librarian", "analyst", "experimentalist", "prover", "writer", "reviewer"}
        assert set(PROFILES.keys()) == expected_roles

    def test_every_role_has_default_profile(self):
        for role, tiers in PROFILES.items():
            assert "default" in tiers, f"Role '{role}' missing default profile"

    def test_profile_fields_are_valid(self):
        for role, tiers in PROFILES.items():
            for tier, profile in tiers.items():
                assert isinstance(profile.model, str) and len(profile.model) > 0
                assert isinstance(profile.backend, str) and profile.backend in BACKENDS
                assert isinstance(profile.max_tokens, int) and profile.max_tokens > 0
                assert 0.0 <= profile.temperature <= 2.0
                assert isinstance(profile.description, str)

    def test_prover_has_reasoning_model(self):
        prover_default = PROFILES["prover"]["default"]
        assert "reasoner" in prover_default.model or "prover" in prover_default.model.lower()

    def test_prover_has_local_profile(self):
        assert "local" in PROFILES["prover"]
        assert PROFILES["prover"]["local"].backend in ("ollama", "vllm")
        assert "goedel" in PROFILES["prover"]["local"].model.lower()

    def test_writer_has_highest_token_budget(self):
        writer_tokens = PROFILES["writer"]["default"].max_tokens
        for role, tiers in PROFILES.items():
            if role != "writer":
                for _, profile in tiers.items():
                    assert profile.max_tokens <= writer_tokens, (
                        f"{role} has higher budget than writer"
                    )


# ──────────────────────────── Routing Logic ───────────────────────────────────


class TestResolveProfile:
    def test_default_tier_returns_default_profile(self):
        profile = resolve_profile("planner")
        assert profile == PROFILES["planner"]["default"]

    def test_explicit_tier_returns_tier_profile(self):
        profile = resolve_profile("planner", "T4-structural")
        assert profile == PROFILES["planner"]["T4-structural"]

    def test_unknown_tier_falls_back_to_default(self):
        profile = resolve_profile("planner", "T99-imaginary")
        assert profile == PROFILES["planner"]["default"]

    def test_unknown_role_returns_fallback_profile(self):
        profile = resolve_profile("nonexistent_role")
        assert profile.model == "deepseek-chat"  # fallback

    def test_prefer_local_returns_local_when_available(self):
        profile = resolve_profile("prover", prefer_local=True)
        assert profile.backend in ("ollama", "vllm")

    def test_prefer_local_returns_default_when_no_local(self):
        profile = resolve_profile("librarian", prefer_local=True)
        assert profile == PROFILES["librarian"]["default"]


class TestResolveWithFallback:
    def test_configured_backend_returns_primary(self):
        # Local backends are always configured
        profile, backend = resolve_with_fallback("prover", prefer_local=True)
        assert backend.is_configured is True

    def test_unconfigured_backend_tries_fallback(self):
        # Clear all API keys to force fallback behavior
        env_overrides = {
            "DEEPSEEK_API_KEY": "",
            "OPENAI_API_KEY": "test-key-for-fallback",
            "ANTHROPIC_API_KEY": "",
        }
        with patch.dict(os.environ, env_overrides, clear=False):
            profile, backend = resolve_with_fallback("librarian")
            # Should either use the original (if configured) or fall back
            assert isinstance(profile, ModelProfile)
            assert isinstance(backend, Backend)


# ──────────────────────────── Backend Inference ───────────────────────────────


class TestInferBackend:
    @pytest.mark.parametrize("model,expected", [
        ("claude-sonnet-4-20250514", "anthropic"),
        ("claude-opus-4-20250514", "anthropic"),
        ("deepseek-chat", "deepseek"),
        ("deepseek-reasoner", "deepseek"),
        ("deepseek-prover-v2:7b", "ollama"),
        ("goedel-prover-v2-32b", "vllm"),
        ("gpt-4o", "openai"),
        ("gpt-4o-mini", "openai"),
        ("o3-mini", "openai"),
        ("llama3", "ollama"),
        ("qwen2.5-coder", "ollama"),
        ("unknown-model", "openai"),
    ])
    def test_infer_backend(self, model: str, expected: str):
        assert _infer_backend(model) == expected


# ──────────────────────────── Health Checks ───────────────────────────────────


class TestHealthChecks:
    def test_unconfigured_backend_reports_unhealthy(self):
        b = Backend(name="test", base_url="http://localhost:1", api_key_env="NONEXISTENT_KEY_XYZ")
        with patch.dict(os.environ, {"NONEXISTENT_KEY_XYZ": ""}, clear=False):
            result = check_backend_health(b, timeout=1.0)
            assert result.healthy is False

    def test_check_all_backends_returns_all(self):
        results = check_all_backends(timeout=0.5)
        assert len(results) == len(BACKENDS)
        for r in results:
            assert "name" in r
            assert "configured" in r
            assert "healthy" in r

    def test_local_unreachable_backend_reports_down(self):
        b = Backend(
            name="test-ollama",
            base_url="http://127.0.0.1:19999",  # unlikely to be running
            api_key_env="NONEXISTENT",
        )
        # Override is_configured for local
        result = check_backend_health(b, timeout=0.5)
        # Either unhealthy (no server) or configured=False
        assert result.healthy is False or result.healthy is None


# ──────────────────────────── CLI Smoke Tests ─────────────────────────────────


class TestCLISmoke:
    def test_profiles_command(self, capsys):
        from model_router import cmd_profiles
        cmd_profiles()
        output = capsys.readouterr().out
        assert "planner" in output
        assert "prover" in output
        assert "deepseek" in output

    def test_backends_command(self, capsys):
        from model_router import cmd_backends
        cmd_backends()
        output = capsys.readouterr().out
        assert "openai" in output
        assert "ollama" in output

    def test_resolve_command(self, capsys):
        from model_router import cmd_resolve
        cmd_resolve("prover", "default", False)
        output = capsys.readouterr().out
        assert "prover" in output
        assert "model" in output
