#!/usr/bin/env python3
"""OMEGA literature adapter.

Provides a bounded, machine-readable retrieval surface for citation fact-checking
and novelty-collision work using the official Semantic Scholar Graph API with an
official arXiv API fallback for unresolved arXiv identifiers.

Usage:
  python scripts/literature_adapter.py lookup 2504.11354
  python scripts/literature_adapter.py lookup ARXIV:2504.11354
  python scripts/literature_adapter.py match-title "Kimina-Prover Preview"
  python scripts/literature_adapter.py search "Semi-Autonomous Mathematics Discovery" --limit 5
"""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any

import yaml

SEMANTIC_SCHOLAR_GRAPH = "https://api.semanticscholar.org/graph/v1"
ARXIV_QUERY = "https://export.arxiv.org/api/query"
USER_AGENT = "OMEGA-literature-adapter/0.4.0 (+https://github.com/KonkovDV/SynAPS)"
DEFAULT_FIELDS = ",".join(
    [
        "title",
        "authors",
        "year",
        "abstract",
        "url",
        "externalIds",
        "citationCount",
        "referenceCount",
        "venue",
        "publicationDate",
        "isOpenAccess",
        "openAccessPdf",
        "citationStyles",
    ]
)
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    return " ".join(value.split())


def _headers(api_key: str | None = None) -> dict[str, str]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key
    return headers


def _fetch_text(url: str, *, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> str:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers=headers or {"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def _fetch_json(url: str, *, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> Any:
    return json.loads(_fetch_text(url, params=params, headers=headers))


def normalize_identifier(identifier: str) -> str:
    raw = identifier.strip()
    if raw.lower().startswith("arxiv:"):
        return f"ARXIV:{raw.split(':', 1)[1]}"
    if raw.lower().startswith(("https://arxiv.org/abs/", "http://arxiv.org/abs/")):
        return f"ARXIV:{raw.rstrip('/').rsplit('/', 1)[-1]}"
    if raw.lower().startswith(("https://doi.org/", "http://dx.doi.org/")):
        return f"DOI:{raw.rstrip('/').rsplit('/', 1)[-1]}"
    if raw.lower().startswith("doi:"):
        return f"DOI:{raw.split(':', 1)[1]}"
    if raw.lower().startswith(("https://", "http://")):
        return f"URL:{raw}"
    if re.fullmatch(r"\d{4}\.\d{4,5}(v\d+)?", raw, flags=re.IGNORECASE):
        return f"ARXIV:{raw}"
    if raw.startswith("10."):
        return f"DOI:{raw}"
    return raw


def _external_id(external_ids: dict[str, Any], key: str) -> str | None:
    for current_key, value in external_ids.items():
        if current_key.lower() == key.lower():
            return value
    return None


def normalize_semantic_scholar_paper(payload: dict[str, Any], *, source: str) -> dict[str, Any]:
    external_ids = payload.get("externalIds") or {}
    return {
        "source": source,
        "paper_id": payload.get("paperId"),
        "title": _clean_text(payload.get("title")),
        "authors": [_clean_text(author.get("name")) for author in payload.get("authors") or [] if author.get("name")],
        "year": payload.get("year"),
        "abstract": _clean_text(payload.get("abstract")),
        "url": payload.get("url"),
        "venue": payload.get("venue") or ((payload.get("journal") or {}).get("name")),
        "citation_count": payload.get("citationCount"),
        "reference_count": payload.get("referenceCount"),
        "external_ids": external_ids,
        "doi": _external_id(external_ids, "DOI"),
        "arxiv_id": _external_id(external_ids, "ArXiv") or _external_id(external_ids, "ARXIV"),
        "publication_date": payload.get("publicationDate"),
        "is_open_access": payload.get("isOpenAccess"),
        "open_access_pdf": ((payload.get("openAccessPdf") or {}).get("url")),
        "bibtex": ((payload.get("citationStyles") or {}).get("bibtex")),
    }


def lookup_semantic_scholar(identifier: str, *, api_key: str | None = None) -> dict[str, Any]:
    normalized = normalize_identifier(identifier)
    payload = _fetch_json(
        f"{SEMANTIC_SCHOLAR_GRAPH}/paper/{urllib.parse.quote(normalized, safe=':/.')}",
        params={"fields": DEFAULT_FIELDS},
        headers=_headers(api_key),
    )
    return normalize_semantic_scholar_paper(payload, source="semantic-scholar")


def search_semantic_scholar(query: str, *, limit: int = 10, api_key: str | None = None) -> dict[str, Any]:
    payload = _fetch_json(
        f"{SEMANTIC_SCHOLAR_GRAPH}/paper/search",
        params={"query": query, "limit": limit, "fields": DEFAULT_FIELDS},
        headers=_headers(api_key),
    )
    return {
        "source": "semantic-scholar-search",
        "query": query,
        "count": len(payload.get("data") or []),
        "papers": [normalize_semantic_scholar_paper(item, source="semantic-scholar-search") for item in payload.get("data") or []],
    }


def match_title_semantic_scholar(query: str, *, api_key: str | None = None) -> dict[str, Any]:
    try:
        payload = _fetch_json(
            f"{SEMANTIC_SCHOLAR_GRAPH}/paper/search/match",
            params={"query": query, "fields": DEFAULT_FIELDS},
            headers=_headers(api_key),
        )
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {
                "source": "semantic-scholar-title-match",
                "query": query,
                "count": 0,
                "papers": [],
            }
        raise
    papers = payload.get("data") or []
    return {
        "source": "semantic-scholar-title-match",
        "query": query,
        "count": len(papers),
        "papers": [normalize_semantic_scholar_paper(item, source="semantic-scholar-title-match") for item in papers],
    }


def _first_text(entry: ET.Element, xpath: str) -> str | None:
    node = entry.find(xpath, ATOM_NS)
    return _clean_text(node.text if node is not None else None)


def lookup_arxiv(identifier: str) -> dict[str, Any]:
    normalized = normalize_identifier(identifier)
    arxiv_id = normalized.split(":", 1)[1] if normalized.startswith("ARXIV:") else normalized
    xml_text = _fetch_text(
        ARXIV_QUERY,
        params={"id_list": arxiv_id, "start": 0, "max_results": 1},
        headers={"User-Agent": USER_AGENT, "Accept": "application/atom+xml"},
    )
    root = ET.fromstring(xml_text)
    entry = root.find("atom:entry", ATOM_NS)
    if entry is None:
        raise LookupError(f"arXiv did not return an entry for '{arxiv_id}'")

    entry_title = _first_text(entry, "atom:title")
    if entry_title == "Error":
        summary = _first_text(entry, "atom:summary") or f"arXiv returned an error for '{arxiv_id}'"
        raise LookupError(summary)

    abs_url = _first_text(entry, "atom:id")
    pdf_url = None
    for link in entry.findall("atom:link", ATOM_NS):
        if link.attrib.get("title") == "pdf":
            pdf_url = link.attrib.get("href")
            break

    doi = _first_text(entry, "arxiv:doi")
    journal_ref = _first_text(entry, "arxiv:journal_ref")
    published = _first_text(entry, "atom:published")
    updated = _first_text(entry, "atom:updated")
    primary_category = None
    primary = entry.find("arxiv:primary_category", ATOM_NS)
    if primary is not None:
        primary_category = primary.attrib.get("term")

    return {
        "source": "arxiv",
        "paper_id": arxiv_id,
        "title": _first_text(entry, "atom:title"),
        "authors": [_clean_text(author.findtext("atom:name", default="", namespaces=ATOM_NS)) for author in entry.findall("atom:author", ATOM_NS)],
        "year": int(published[:4]) if published else None,
        "abstract": _first_text(entry, "atom:summary"),
        "url": abs_url,
        "venue": journal_ref,
        "citation_count": None,
        "reference_count": None,
        "external_ids": {"ARXIV": arxiv_id, **({"DOI": doi} if doi else {})},
        "doi": doi,
        "arxiv_id": arxiv_id,
        "publication_date": published[:10] if published else None,
        "updated": updated[:10] if updated else None,
        "primary_category": primary_category,
        "journal_ref": journal_ref,
        "pdf_url": pdf_url,
        "bibtex": None,
    }


def lookup_auto(identifier: str, *, api_key: str | None = None) -> dict[str, Any]:
    try:
        return lookup_semantic_scholar(identifier, api_key=api_key)
    except (LookupError, urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError):
        normalized = normalize_identifier(identifier)
        if normalized.startswith("ARXIV:"):
            return lookup_arxiv(normalized)
        raise


def dump_payload(payload: dict[str, Any], *, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(payload, indent=2, ensure_ascii=False)
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="omega-literature", description="OMEGA literature retrieval adapter")
    parser.add_argument("--output-format", choices=("yaml", "json"), default="yaml")
    parser.add_argument("--api-key", default=os.getenv("SEMANTIC_SCHOLAR_API_KEY"))
    subparsers = parser.add_subparsers(dest="action", required=True)

    lookup_parser = subparsers.add_parser("lookup", help="Resolve a DOI/arXiv/S2 paper identifier")
    lookup_parser.add_argument("identifier")
    lookup_parser.add_argument("--source", choices=("auto", "semantic-scholar", "arxiv"), default="auto")
    lookup_parser.add_argument("--problem-id")

    search_parser = subparsers.add_parser("search", help="Search Semantic Scholar by plain-text query")
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int, default=10)
    search_parser.add_argument("--problem-id")

    match_parser = subparsers.add_parser("match-title", help="Get the closest title match from Semantic Scholar")
    match_parser.add_argument("query")
    match_parser.add_argument("--problem-id")

    args = parser.parse_args(argv)

    if args.action == "lookup":
        if args.source == "semantic-scholar":
            paper = lookup_semantic_scholar(args.identifier, api_key=args.api_key)
        elif args.source == "arxiv":
            paper = lookup_arxiv(args.identifier)
        else:
            paper = lookup_auto(args.identifier, api_key=args.api_key)
        payload = {
            "query": args.identifier,
            "source": paper["source"],
            "count": 1,
            "paper": paper,
        }
        if args.problem_id:
            payload["problem_id"] = args.problem_id
    elif args.action == "search":
        payload = search_semantic_scholar(args.query, limit=args.limit, api_key=args.api_key)
        if args.problem_id:
            payload["problem_id"] = args.problem_id
    else:
        payload = match_title_semantic_scholar(args.query, api_key=args.api_key)
        if args.problem_id:
            payload["problem_id"] = args.problem_id

    print(dump_payload(payload, output_format=args.output_format))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())