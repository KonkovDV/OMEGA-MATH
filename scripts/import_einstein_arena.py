#!/usr/bin/env python3
"""Import Einstein Arena benchmark table into OMEGA collections.

Fetches the problem table from togethercomputer/EinsteinArena-new-SOTA README,
parses benchmark rows, and writes a normalized collection YAML file under
registry/collections/.

Usage:
  python scripts/import_einstein_arena.py
  python scripts/import_einstein_arena.py --dry-run
  python scripts/import_einstein_arena.py --url <raw-readme-url> --output <path>
    python scripts/import_einstein_arena.py --readme-file .benchmarks/einstein-arena-readme.md --repo-dir ../EinsteinArena-new-SOTA
"""

from __future__ import annotations

import argparse
import re
import shutil
import unicodedata
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_URL = "https://raw.githubusercontent.com/togethercomputer/EinsteinArena-new-SOTA/main/README.md"
DEFAULT_OUTPUT = REPO_ROOT / "registry" / "collections" / "einstein-arena-benchmarks.yaml"
DEFAULT_LOCAL_README = REPO_ROOT / ".benchmarks" / "einstein-arena-readme.md"
DEFAULT_SOLUTIONS_OUT = REPO_ROOT / "research" / "benchmarks" / "einstein-arena"
DEFAULT_ALIASES_PATH = REPO_ROOT / "registry" / "collections" / "einstein-arena-aliases.yaml"
DEFAULT_ALIASES = {
    "tammes-problem": "thomson-problem",
}


@dataclass(frozen=True)
class EinsteinRow:
    """One parsed row from EinsteinArena README problem table."""

    name: str
    slug: str
    objective: str
    our_result: str
    previous_best: str
    improvement: str


def fetch_text(url: str, timeout_seconds: int = 20) -> str:
    """Fetch UTF-8 text from a URL."""
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        return resp.read().decode("utf-8")


def load_source_markdown(url: str, readme_file: str | None) -> str:
    """Load markdown from local file (preferred) or fetch over network.

    Order:
      1) explicit --readme-file
      2) network URL
      3) default local cache file if present
    """
    if readme_file:
        path = Path(readme_file)
        return path.read_text(encoding="utf-8")

    try:
        return fetch_text(url)
    except urllib.error.URLError:
        if DEFAULT_LOCAL_README.exists():
            return DEFAULT_LOCAL_README.read_text(encoding="utf-8")
        raise


def clean_metric(raw: str) -> str:
    """Normalize markdown metric values to plain strings.

    Examples:
      "**1.280932**\\*" -> "1.280932"
      "−0.000005" -> "-0.000005"
      "—" -> "n/a"
    """
    value = raw.strip()
    value = value.replace("**", "")
    value = value.replace("\\*", "")
    value = value.replace("*", "")
    value = value.replace("†", "")
    value = value.replace("−", "-")
    value = value.replace("–", "-")
    if value in {"—", "-", ""}:
        return "n/a"
    return value.strip()


def slugify_problem_name(name: str) -> str:
    """Convert a plain-text problem name into a stable slug candidate."""
    normalized = unicodedata.normalize("NFKD", name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    collapsed = re.sub(r"\s*\([^)]*\)", "", ascii_name)
    slug = re.sub(r"[^a-z0-9]+", "-", collapsed.lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug)


def normalize_problem_slug(raw_slug: str) -> str:
    """Normalize README href/path slugs to OMEGA collection keys."""
    slug = raw_slug.strip().split("?", 1)[0].split("#", 1)[0]
    return slug.strip("/")


def split_markdown_row(line: str) -> list[str]:
    row = line.strip()
    if not row.startswith("|"):
        return []
    cells = [cell.strip() for cell in row.strip("|").split("|")]
    return cells


def is_separator_row(cells: list[str]) -> bool:
    if not cells:
        return False
    compact = [cell.replace(" ", "") for cell in cells]
    return all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in compact if cell)


def parse_problem_cell(cell: str) -> tuple[str, str] | None:
    cell_text = cell.strip()

    markdown_match = re.search(r"\[(?P<name>[^\]]+)\]\((?P<slug>[^)]+)\)", cell_text)
    if markdown_match:
        name = markdown_match.group("name").strip()
        slug = normalize_problem_slug(markdown_match.group("slug"))
        if name and slug:
            return name, slug

    html_match = re.search(
        r"<a\s+[^>]*href=[\"'](?P<slug>[^\"']+)[\"'][^>]*>(?P<name>.*?)</a>",
        cell_text,
        flags=re.IGNORECASE,
    )
    if html_match:
        raw_name = re.sub(r"<[^>]+>", "", html_match.group("name"))
        name = raw_name.strip()
        slug = normalize_problem_slug(html_match.group("slug"))
        if name and slug:
            return name, slug

    slug_hint_match = re.search(r"^(?P<name>.+?)\s*\((?P<slug>[a-z0-9][a-z0-9\-/]+)\)\s*$", cell_text, re.IGNORECASE)
    if slug_hint_match:
        name = slug_hint_match.group("name").strip()
        slug = normalize_problem_slug(slug_hint_match.group("slug"))
        if name and slug:
            return name, slug

    plain_name = re.sub(r"<[^>]+>", "", cell_text)
    plain_name = plain_name.replace("**", "").replace("*", "").replace("`", "").strip()
    if not plain_name:
        return None

    inferred_slug = slugify_problem_name(plain_name)
    if inferred_slug:
        return plain_name, inferred_slug
    return None


def load_aliases(aliases_file: Path | None = None) -> dict[str, str]:
    aliases = dict(DEFAULT_ALIASES)
    path = aliases_file or DEFAULT_ALIASES_PATH
    if not path.exists():
        return aliases

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raw_aliases: dict[str, Any]
    if isinstance(data, dict) and isinstance(data.get("aliases"), dict):
        raw_aliases = data["aliases"]
    elif isinstance(data, dict):
        raw_aliases = data
    else:
        return aliases

    for source_slug, target_problem in raw_aliases.items():
        if isinstance(source_slug, str) and isinstance(target_problem, str):
            aliases[source_slug.strip()] = target_problem.strip()

    return aliases


def parse_problem_rows(markdown: str) -> list[EinsteinRow]:
    """Parse EinsteinArena README table rows into structured records."""
    rows: list[EinsteinRow] = []
    required_headers = {
        "problem": "problem",
        "objective": "objective",
        "our result": "our_result",
        "previous best": "previous_best",
        "improvement": "improvement",
    }

    header_map: dict[str, int] | None = None
    for line in markdown.splitlines():
        cells = split_markdown_row(line)
        if not cells:
            if header_map is not None and rows:
                break
            continue

        if header_map is None:
            normalized = {value.strip().lower(): idx for idx, value in enumerate(cells)}
            if all(header in normalized for header in required_headers):
                header_map = {key: normalized[header] for header, key in required_headers.items()}
            continue

        if is_separator_row(cells):
            continue

        max_required_index = max(header_map.values())
        if len(cells) <= max_required_index:
            continue

        problem_cell = cells[header_map["problem"]]
        parsed_problem = parse_problem_cell(problem_cell)
        if not parsed_problem:
            continue

        name, slug = parsed_problem
        row = EinsteinRow(
            name=name,
            slug=slug,
            objective=cells[header_map["objective"]].strip().lower(),
            our_result=clean_metric(cells[header_map["our_result"]]),
            previous_best=clean_metric(cells[header_map["previous_best"]]),
            improvement=clean_metric(cells[header_map["improvement"]]),
        )
        rows.append(row)

    return rows


def load_domain_ids() -> set[str]:
    """Load canonical problem IDs from active domain files."""
    domain_ids: set[str] = set()
    domains_dir = REPO_ROOT / "registry" / "domains"

    for path in sorted(domains_dir.glob("*.yaml")):
        text_head = path.read_text(encoding="utf-8")[:400].lower()
        if path.name == "other-domains.yaml" or ("deprecated" in text_head and "redirect" in text_head):
            continue

        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for problem in data.get("problems", []):
            pid = problem.get("id")
            if isinstance(pid, str) and pid:
                domain_ids.add(pid)

    return domain_ids


def infer_registry_link(slug: str, domain_ids: set[str], aliases: dict[str, str] | None = None) -> str | None:
    """Infer registry_id when Einstein slug directly matches known OMEGA IDs."""
    if slug in domain_ids:
        return slug

    alias = (aliases or DEFAULT_ALIASES).get(slug)
    if alias and alias in domain_ids:
        return alias

    return None


def copy_solution_snapshots(
    rows: list[EinsteinRow],
    donor_repo_dir: Path,
    destination_root: Path,
) -> dict[str, list[str]]:
    """Copy per-problem solution files from local donor checkout.

    Returns mapping: slug -> list of copied relative file paths.
    """
    copied: dict[str, list[str]] = {}
    for row in rows:
        source_solutions = donor_repo_dir / row.slug / "solutions"
        if not source_solutions.exists() or not source_solutions.is_dir():
            continue

        target_solutions = destination_root / row.slug / "solutions"
        target_solutions.mkdir(parents=True, exist_ok=True)

        copied_files: list[str] = []
        for source_file in sorted(source_solutions.rglob("*")):
            if not source_file.is_file():
                continue
            relative = source_file.relative_to(source_solutions)
            target_file = target_solutions / relative
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target_file)

            try:
                rel_to_repo = target_file.relative_to(REPO_ROOT)
                copied_files.append(rel_to_repo.as_posix())
            except ValueError:
                copied_files.append(target_file.as_posix())

        if copied_files:
            copied[row.slug] = copied_files

    return copied


def build_collection(
    rows: list[EinsteinRow],
    source_url: str,
    solution_files: dict[str, list[str]] | None = None,
    aliases: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build the OMEGA collection payload from parsed rows."""
    domain_ids = load_domain_ids()
    alias_map = aliases or load_aliases()
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    problems: list[dict[str, Any]] = []
    solution_files = solution_files or {}
    for row in rows:
        entry: dict[str, Any] = {
            "id": f"einstein-arena-{row.slug}",
            "name": row.name,
            "status": "open",
            "objective": row.objective,
            "our_result": row.our_result,
            "previous_best": row.previous_best,
            "improvement": row.improvement,
            "source_problem_path": row.slug,
            "source_repo": "togethercomputer/EinsteinArena-new-SOTA",
            "evidence_class": "E1",
            "note": "Extracted from EinsteinArena-new-SOTA README table. Scores are benchmark snapshots and may lag live leaderboard.",
        }

        registry_id = infer_registry_link(row.slug, domain_ids, alias_map)
        if registry_id:
            entry["registry_id"] = registry_id

        copied = solution_files.get(row.slug)
        if copied:
            entry["solution_files"] = copied
            entry["solution_source"] = "local-donor-checkout"

        problems.append(entry)

    return {
        "collection": "einstein-arena-benchmarks",
        "status": "active",
        "source": source_url,
        "last_synced": now,
        "problems": problems,
    }


def write_collection(payload: dict[str, Any], output_path: Path) -> None:
    """Write normalized collection YAML file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    header = [
        "# Einstein Arena Benchmarks — Quick Reference",
        "# Auto-generated from togethercomputer/EinsteinArena-new-SOTA README table",
        "# Canonical OMEGA records remain in registry/domains/*.yaml",
        "",
    ]
    body = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    output_path.write_text("\n".join(header) + body, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="omega-import-einstein-arena",
        description="Import EinsteinArena benchmark table into OMEGA collection YAML.",
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="Raw README URL to parse")
    parser.add_argument("--readme-file", default=None, help="Local README.md snapshot path")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output collection YAML path")
    parser.add_argument("--aliases-file", default=str(DEFAULT_ALIASES_PATH), help="Path to Einstein Arena slug aliases YAML")
    parser.add_argument("--repo-dir", default=None, help="Local checkout path of EinsteinArena-new-SOTA for copying solutions/")
    parser.add_argument("--solutions-out", default=str(DEFAULT_SOLUTIONS_OUT), help="Destination root for copied solution snapshots")
    parser.add_argument("--dry-run", action="store_true", help="Print YAML instead of writing file")
    args = parser.parse_args(argv)

    markdown = load_source_markdown(args.url, args.readme_file)
    rows = parse_problem_rows(markdown)
    if not rows:
        print("ERROR: No EinsteinArena problem rows found in source README")
        return 1

    copied_solution_files: dict[str, list[str]] = {}
    if args.repo_dir:
        copied_solution_files = copy_solution_snapshots(
            rows,
            Path(args.repo_dir),
            Path(args.solutions_out),
        )

    aliases = load_aliases(Path(args.aliases_file))
    payload = build_collection(rows, args.url, copied_solution_files, aliases)

    if args.dry_run:
        print(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True))
    else:
        output_path = Path(args.output)
        write_collection(payload, output_path)
        copied_count = sum(len(v) for v in copied_solution_files.values())
        print(f"Imported {len(rows)} EinsteinArena rows -> {output_path}")
        if copied_count:
            print(f"Copied {copied_count} solution files from local donor checkout")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
