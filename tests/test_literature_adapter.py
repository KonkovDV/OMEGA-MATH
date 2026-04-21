#!/usr/bin/env python3
"""Unit tests for the OMEGA literature adapter."""

from __future__ import annotations

import io
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from literature_adapter import match_title_semantic_scholar, normalize_identifier, lookup_arxiv, lookup_auto, search_semantic_scholar  # type: ignore
from literature_adapter import build_novelty_packet  # type: ignore


class _FakeResponse:
    def __init__(self, body: str) -> None:
        self._body = body.encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


class LiteratureAdapterTests(unittest.TestCase):
    def test_normalize_identifier_supports_url_backed_semantic_scholar_ids(self) -> None:
        self.assertEqual(
            normalize_identifier("https://www.semanticscholar.org/paper/abc123"),
            "URL:https://www.semanticscholar.org/paper/abc123",
        )

    def test_lookup_auto_prefers_semantic_scholar_and_preserves_bibtex(self) -> None:
        semantic_scholar_payload = """
        {
          "paperId": "paper-1",
          "title": "Kimina-Prover Preview",
          "authors": [{"name": "Haiming Wang"}, {"name": "Mert Unsal"}],
          "year": 2025,
          "abstract": "formal reasoning",
          "url": "https://www.semanticscholar.org/paper/paper-1",
          "externalIds": {"ArXiv": "2504.11354", "DOI": "10.48550/arXiv.2504.11354"},
          "citationCount": 12,
          "referenceCount": 34,
          "citationStyles": {"bibtex": "@article{kimina}"}
        }
        """

        with patch("urllib.request.urlopen", return_value=_FakeResponse(semantic_scholar_payload)) as mocked:
            paper = lookup_auto("2504.11354")

        self.assertEqual(paper["source"], "semantic-scholar")
        self.assertEqual(paper["arxiv_id"], "2504.11354")
        self.assertEqual(paper["bibtex"], "@article{kimina}")
        request = mocked.call_args.args[0]
        self.assertIn("ARXIV:2504.11354", request.full_url)

    def test_lookup_auto_falls_back_to_arxiv_atom(self) -> None:
        arxiv_payload = """
        <feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
          <entry>
            <id>http://arxiv.org/abs/2601.22401v3</id>
            <published>2026-01-15T00:00:00Z</published>
            <updated>2026-02-01T00:00:00Z</updated>
            <title>Semi-Autonomous Mathematics Discovery with Gemini</title>
            <summary>abstract text</summary>
            <author><name>Tony Feng</name></author>
            <author><name>Trieu Trinh</name></author>
            <arxiv:primary_category term="cs.AI" scheme="http://arxiv.org/schemas/atom" />
            <arxiv:journal_ref>arXiv preprint</arxiv:journal_ref>
            <arxiv:doi>10.48550/arXiv.2601.22401</arxiv:doi>
            <link href="http://arxiv.org/abs/2601.22401v3" rel="alternate" type="text/html" />
            <link title="pdf" href="http://arxiv.org/pdf/2601.22401v3" rel="related" type="application/pdf" />
          </entry>
        </feed>
        """

        http_error = urllib.error.HTTPError(
            url="https://api.semanticscholar.org/graph/v1/paper/ARXIV:2601.22401",
            code=404,
            msg="not found",
            hdrs=None,
            fp=io.BytesIO(b"{}"),
        )

        with patch("urllib.request.urlopen", side_effect=[http_error, _FakeResponse(arxiv_payload)]):
            paper = lookup_auto("ARXIV:2601.22401")

        self.assertEqual(paper["source"], "arxiv")
        self.assertEqual(paper["arxiv_id"], "2601.22401")
        self.assertEqual(paper["doi"], "10.48550/arXiv.2601.22401")
        self.assertEqual(paper["authors"], ["Tony Feng", "Trieu Trinh"])

    def test_lookup_arxiv_raises_on_atom_error_feed(self) -> None:
        error_feed = """
        <feed xmlns="http://www.w3.org/2005/Atom" xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">
            <entry>
                <id>http://arxiv.org/api/errors#incorrect_id_format</id>
                <title>Error</title>
                <summary>incorrect id format for 1234.12345</summary>
            </entry>
        </feed>
        """

        with patch("urllib.request.urlopen", return_value=_FakeResponse(error_feed)):
            with self.assertRaisesRegex(LookupError, "incorrect id format"):
                lookup_arxiv("ARXIV:1234.12345")

    def test_search_and_match_title_normalize_paper_lists(self) -> None:
        search_payload = """
        {"data": [{"paperId": "paper-2", "title": "Towards Autonomous Mathematics Research", "authors": [{"name": "Tony Feng"}], "year": 2026, "url": "https://example.com", "externalIds": {}, "citationStyles": {}}]}
        """
        match_payload = """
        {"data": [{"paperId": "paper-3", "title": "The Denario project", "authors": [{"name": "Francisco Villaescusa-Navarro"}], "year": 2025, "url": "https://example.org", "externalIds": {}, "citationStyles": {}}]}
        """

        with patch("urllib.request.urlopen", side_effect=[_FakeResponse(search_payload), _FakeResponse(match_payload)]):
            search_result = search_semantic_scholar("autonomous mathematics", limit=5)
            match_result = match_title_semantic_scholar("The Denario project")

        self.assertEqual(search_result["count"], 1)
        self.assertEqual(search_result["papers"][0]["title"], "Towards Autonomous Mathematics Research")
        self.assertEqual(match_result["count"], 1)
        self.assertEqual(match_result["papers"][0]["authors"], ["Francisco Villaescusa-Navarro"])

    def test_match_title_returns_empty_result_on_404(self) -> None:
        http_error = urllib.error.HTTPError(
            url="https://api.semanticscholar.org/graph/v1/paper/search/match?query=missing",
            code=404,
            msg="Title match not found",
            hdrs=None,
            fp=io.BytesIO(b"{}"),
        )

        with patch("urllib.request.urlopen", side_effect=http_error):
            result = match_title_semantic_scholar("missing title")

        self.assertEqual(result["count"], 0)
        self.assertEqual(result["papers"], [])

    def test_build_novelty_packet_is_stable_and_deduplicated(self) -> None:
        papers = [
            {
                "paper_id": "p1",
                "title": "Collision Candidate",
                "authors": ["A"],
                "year": 2026,
                "citation_count": 25,
                "doi": "10.1000/abc",
                "arxiv_id": None,
                "url": "https://example.org/p1",
            },
            {
                "paper_id": "p2",
                "title": "Collision Candidate Duplicate",
                "authors": ["A"],
                "year": 2025,
                "citation_count": 5,
                "doi": "10.1000/abc",
                "arxiv_id": None,
                "url": "https://example.org/p2",
            },
            {
                "paper_id": "p3",
                "title": "Fresh but low-citation idea",
                "authors": ["B"],
                "year": 2026,
                "citation_count": 2,
                "doi": None,
                "arxiv_id": "2601.00001",
                "url": "https://example.org/p3",
            },
        ]

        packet = build_novelty_packet(
            "autonomous mathematics",
            papers,
            problem_id="erdos-straus",
            max_items=5,
        )

        self.assertEqual(packet["source"], "omega-literature-novelty-packet")
        self.assertEqual(packet["count"], 2)
        self.assertEqual(packet["problem_id"], "erdos-straus")
        self.assertEqual(packet["candidates"][0]["paper_id"], "p1")
        self.assertEqual(packet["candidates"][0]["collision_risk"], "medium")


if __name__ == "__main__":
    unittest.main()