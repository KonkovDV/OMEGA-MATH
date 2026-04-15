# OMEGA Literature Adapter

Defines the contract for programmatic literature retrieval and citation fact-checking in the OMEGA standalone runtime.

## Purpose

The literature adapter provides a bounded, machine-readable retrieval surface for:

- citation fact-checking against primary metadata
- novelty-collision screening before plan or publication work
- BibTeX retrieval when authoritative upstream metadata exposes it

The adapter uses the official Semantic Scholar Graph API first and falls back to the official arXiv API for unresolved arXiv identifiers.

## Official Grounding (April 2026)

- **Semantic Scholar Graph API** supports `paper/search`, `paper/search/match`, and `paper/{paper_id}` with requested fields such as `authors`, `externalIds`, `citationCount`, `referenceCount`, and `citationStyles.bibtex`.
- **Semantic Scholar identifiers** officially support `ARXIV:<id>`, `DOI:<doi>`, URL-backed ids, and Semantic Scholar paper ids.
- **Semantic Scholar API keys** are optional but, when used, must be sent in the `x-api-key` header.
- **arXiv API** supports `id_list` and `search_query` over Atom feeds, exposing `title`, `summary`, ordered `author` entries, `doi`, `journal_ref`, and PDF/abstract links.
- **arXiv operational guidance** asks clients making repeated calls to incorporate a 3-second delay and to avoid unnecessary repeated requests for unchanged queries.

## Adapter Contract

### Input

```yaml
action: "lookup | search | match-title"
identifier: "ARXIV:2504.11354 | DOI:10... | plain arXiv id | title query"
query: "plain-text paper query"
limit: 10
problem_id: "optional OMEGA registry id"
source: "auto | semantic-scholar | arxiv"
output_format: "yaml | json"
api_key: "optional Semantic Scholar key"
```

### Output

```yaml
query: "echoed query or identifier"
source: "semantic-scholar | semantic-scholar-search | semantic-scholar-title-match | arxiv"
count: 1
problem_id: "optional"
paper:
  paper_id: "paper or arXiv identifier"
  title: "..."
  authors: ["..."]
  year: 2026
  abstract: "..."
  url: "..."
  venue: "..."
  citation_count: 12
  reference_count: 34
  external_ids: {}
  doi: "..."
  arxiv_id: "..."
  publication_date: "YYYY-MM-DD"
  bibtex: "@article{...}" | null
papers: []
```

## Actions

### `lookup`

Resolve a single identifier.

Precedence:

1. normalize DOI / arXiv / URL-style identifiers
2. query Semantic Scholar `paper/{paper_id}` with official fields
3. if the identifier is arXiv-based and Semantic Scholar fails, query arXiv `id_list`

Use this for bibliography repair, author/title verification, and authoritative BibTeX capture when available.

### `search`

Run a plain-text Semantic Scholar `paper/search` query and return a normalized paper list.

Use this for bounded literature reconnaissance and novelty-collision scouting.

### `match-title`

Run Semantic Scholar `paper/search/match` and return the closest title match.

If the official endpoint returns `404 Title match not found`, the adapter normalizes
that into `count: 0` with an empty `papers` list instead of crashing the operator workflow.

Use this when you already have a candidate title string and want the smallest high-confidence confirmation call.

## Source Rules

1. Prefer Semantic Scholar for structured metadata and BibTeX when the paper is indexed there.
2. Prefer arXiv fallback for fresh preprints or unresolved arXiv ids.
3. Treat adapter output as evidence input, not as proof of novelty by itself.
4. If metadata disagrees across sources, persist the disagreement in `citation_evidence.md` rather than silently picking a winner.
5. When arXiv returns an Atom error feed, treat it as a lookup failure, not as paper metadata.

## Integration Points

- `research/OMEGA_SOTA_BIBLIOGRAPHY_2026_04_05.md` fact-check passes
- problem-local `input_files/literature.md`
- problem-local `input_files/citation_evidence.md`
- future novelty packet generation in the Phase 3 literature lane