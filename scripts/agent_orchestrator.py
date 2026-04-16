#!/usr/bin/env python3
"""OMEGA Agent Orchestrator — minimal LLM-backed agent execution engine.

Reads agent role definitions from agents/*.yaml, constructs prompts with problem
context, invokes an LLM API, parses output into the expected artifact format, and
advances the workflow state machine.

Design grounded in:
- Denario multi-agent pipeline (arXiv:2510.26887)
- Numina-Lean-Agent agentic pattern (arXiv:2601.14027)
- Aletheia iterative verify-revise cycle (arXiv:2602.10177)
- OMEGA 7-agent team architecture (agents/team.yaml)

Supports: OpenAI-compatible APIs (OpenAI, DeepSeek, local via LM Studio/Ollama),
          Anthropic Claude API, and LiteLLM universal router.

Usage:
  python scripts/agent_orchestrator.py run <problem-id> --stage plan
  python scripts/agent_orchestrator.py run <problem-id> --stage experiment --model deepseek-chat
  python scripts/agent_orchestrator.py dispatch <problem-id> --role experimentalist
  python scripts/agent_orchestrator.py pipeline <problem-id> --from-stage plan --to-stage results
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

# Import model router for profile-based routing
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model_router import resolve_with_fallback  # noqa: E402

# Stage → agent role mapping (derived from team.yaml at import time)
STAGE_TO_ROLE: dict[str, str] = {
    "brief": "planner",
    "novelty": "librarian",
    "triage": "planner",
    "plan": "planner",
    "experiment": "experimentalist",
    "prove": "prover",
    "survey": "analyst",
    "results": "analyst",
    "paper": "writer",
    "referee": "reviewer",
}

DEFAULT_PIPELINE_STAGES = ["brief", "novelty", "triage", "plan", "experiment", "results", "paper", "referee"]
PROOF_FIRST_PIPELINE_STAGES = ["brief", "novelty", "triage", "plan", "prove", "results", "paper", "referee"]
DUAL_LANE_PIPELINE_STAGES = ["brief", "novelty", "triage", "plan", "experiment", "prove", "results", "paper", "referee"]

# Maximum output tokens per role (budget guardrails)
ROLE_TOKEN_BUDGET: dict[str, int] = {
    "planner": 2000,
    "librarian": 3000,
    "analyst": 4000,
    "experimentalist": 4000,
    "prover": 6000,
    "writer": 8000,
    "reviewer": 3000,
}

DEFAULT_MODEL = "deepseek-chat"
DEFAULT_TEMPERATURE = 0.3

STAGES_REQUIRING_WORKSPACE = {
    "novelty",
    "triage",
    "plan",
    "experiment",
    "prove",
    "survey",
    "results",
    "paper",
    "referee",
}

BASE_REQUIRED_WORKSPACE_FILES = {
    "README.md",
    "input_files/data_description.md",
}

STAGE_REQUIRED_WORKSPACE_FILES: dict[str, set[str]] = {
    "novelty": {"input_files/literature.md", "input_files/citation_evidence.md"},
    "prove": {"input_files/proof_obligations.md", "input_files/statement_spec.md"},
    "results": {"input_files/literature.md", "input_files/citation_evidence.md"},
    "paper": {"input_files/literature.md", "input_files/citation_evidence.md"},
    "referee": {"input_files/literature.md", "input_files/citation_evidence.md"},
}

WORKSPACE_FILE_TEMPLATES: dict[str, str] = {
    "README.md": "# Research Workspace\n\nStatus: active\n",
    "input_files/data_description.md": "# Problem Brief\n\n## Problem Statement\n\n## Success Condition\n",
    "input_files/literature.md": "# Literature Packet\n\n## Seed Papers\n\n## Known Results\n",
    "input_files/citation_evidence.md": "# Citation Evidence\n\n## Supporting Citations\n\n## Contrasting Citations\n",
    "input_files/proof_obligations.md": "# Proof Obligations\n\n## Load-Bearing Claims\n\n## Deferred Risks\n",
    "input_files/statement_spec.md": (
        "# Statement Specification\n\n"
        "## Claim Label\n\n"
        "## Formal Statement Draft\n\n"
        "## Assumptions\n\n"
        "## Acceptance Rule\n"
        "- proof must close against this statement without broadening assumptions\n"
    ),
}


# ──────────────────────────── Agent Definition Loading ────────────────────────

def load_agent_definition(role: str) -> dict[str, Any]:
    """Load an agent YAML definition from agents/<role>.yaml."""
    agent_path = REPO_ROOT / "agents" / f"{role}.yaml"
    if not agent_path.exists():
        raise FileNotFoundError(f"Agent definition not found: {agent_path}")
    return yaml.safe_load(agent_path.read_text(encoding="utf-8"))


def load_team_config() -> dict[str, Any]:
    """Load the team orchestration config."""
    team_path = REPO_ROOT / "agents" / "team.yaml"
    return yaml.safe_load(team_path.read_text(encoding="utf-8"))


def load_benchmark_snapshot(problem_id: str) -> dict[str, Any] | None:
    """Load EinsteinArena benchmark snapshot for a canonical OMEGA problem ID."""
    path = REPO_ROOT / "registry" / "collections" / "einstein-arena-benchmarks.yaml"
    if not path.exists():
        return None

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for item in data.get("problems", []):
        if not isinstance(item, dict):
            continue
        if item.get("registry_id") == problem_id:
            return item
        if item.get("source_problem_path") == problem_id:
            return item
        if item.get("id") == problem_id:
            return item

    return None


# ──────────────────────────── Problem Context Assembly ────────────────────────

def load_problem_context(problem_id: str) -> dict[str, Any]:
    """Assemble full problem context from registry + workspace."""
    context: dict[str, Any] = {
        "problem_id": problem_id,
        "registry": None,
        "workspace": None,
        "workflow": None,
        "prior_runs": [],
        "triage": None,
        "benchmark": None,
    }

    # Load from registry domains
    domains_dir = REPO_ROOT / "registry" / "domains"
    if domains_dir.exists():
        for domain_file in sorted(domains_dir.glob("*.yaml")):
            data = yaml.safe_load(domain_file.read_text(encoding="utf-8")) or {}
            for problem in data.get("problems", []):
                if isinstance(problem, dict) and problem.get("id") == problem_id:
                    context["registry"] = problem
                    context["registry"]["domain"] = domain_file.stem
                    break
            if context["registry"]:
                break

    # Load triage matrix entry
    triage_path = REPO_ROOT / "registry" / "triage-matrix.yaml"
    if triage_path.exists():
        triage_data = yaml.safe_load(triage_path.read_text(encoding="utf-8")) or {}
        tier_key_map = {
            "tier_1_computational": "T1-computational",
            "tier_2_experimental": "T2-experimental",
            "tier_3_pattern": "T3-pattern",
            "tier_4_structural": "T4-structural",
            "tier_5_foundational": "T5-foundational",
        }
        for key, entries in triage_data.items():
            if isinstance(entries, list):
                tier = tier_key_map.get(str(key))
                for entry in entries:
                    if isinstance(entry, dict) and entry.get("id") == problem_id:
                        entry_copy = dict(entry)
                        if tier:
                            entry_copy["tier"] = tier
                        context["triage"] = entry_copy
                        break
            if context["triage"]:
                break

    # Load workspace data
    workspace_root = REPO_ROOT / "research" / "active" / problem_id
    if workspace_root.exists():
        context["workspace"] = str(workspace_root)

        # Load workflow state
        wf_path = workspace_root / "control" / "workflow-state.yaml"
        if wf_path.exists():
            context["workflow"] = yaml.safe_load(wf_path.read_text(encoding="utf-8"))

        # Load prior run summaries from experiment ledger
        ledger_path = workspace_root / "experiments" / "ledger.yaml"
        if ledger_path.exists():
            ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
            if isinstance(ledger, dict):
                runs = ledger.get("runs", [])
            elif isinstance(ledger, list):
                runs = ledger
            else:
                runs = []
            if isinstance(runs, list):
                context["prior_runs"] = runs[-5:]  # Last 5 runs for context

        # Load README for problem description
        readme_path = workspace_root / "README.md"
        if readme_path.exists():
            context["problem_description"] = readme_path.read_text(encoding="utf-8")

        # Load proof obligations if they exist
        obligations_path = workspace_root / "input_files" / "proof_obligations.md"
        if obligations_path.exists():
            context["proof_obligations"] = obligations_path.read_text(encoding="utf-8")

        # Load statement specification for statement/proof split governance
        statement_spec_path = workspace_root / "input_files" / "statement_spec.md"
        if statement_spec_path.exists():
            context["statement_spec"] = statement_spec_path.read_text(encoding="utf-8")

    # Load external benchmark snapshot (if available)
    context["benchmark"] = load_benchmark_snapshot(problem_id)

    return context


# ──────────────────────────── Prompt Construction ─────────────────────────────

def build_system_prompt(agent_def: dict[str, Any]) -> str:
    """Construct the system prompt from the agent definition."""
    role = agent_def.get("role", "researcher")
    purpose = agent_def.get("purpose", "assist with research")
    inputs_desc = ", ".join(agent_def.get("inputs", []))
    outputs_desc = ", ".join(agent_def.get("outputs", []))
    criteria = "\n".join(f"- {c}" for c in agent_def.get("success_criteria", []))

    return f"""You are an OMEGA research agent acting as: {role}

Purpose: {purpose}

Expected inputs: {inputs_desc}
Expected outputs: {outputs_desc}

Success criteria:
{criteria}

Rules:
- Output structured YAML at the end of your response in a ```yaml block.
- Separate reasoning from output: think first, then produce the artifact.
- Evidence class: label every factual claim as R0 (machine-verified), R1 (reproducible computation),
  E1 (external reference), E2 (LLM-assisted, requires verification), or H (human judgment).
- Anti-overclaiming: never say "proved" without formal verification. Use "candidate proof",
  "computational evidence", or "conjecture supported by" instead.
- Reproducibility: include all parameters, seeds, and commands needed to reproduce results.
"""


def build_user_prompt(
    stage: str,
    context: dict[str, Any],
    *,
    extra_instructions: str = "",
) -> str:
    """Construct the user prompt with problem context for a specific stage."""
    problem_id = context["problem_id"]
    registry = context.get("registry") or {}
    triage = context.get("triage") or {}
    workflow = context.get("workflow") or {}
    prior_runs = context.get("prior_runs", [])
    benchmark = context.get("benchmark") or {}

    # Build context sections
    sections: list[str] = []
    sections.append(f"# Stage: {stage}")
    sections.append(f"Problem ID: {problem_id}")

    if registry:
        sections.append(f"\n## Problem Definition")
        sections.append(f"Title: {registry.get('title', 'Unknown')}")
        sections.append(f"Domain: {registry.get('domain', 'Unknown')}")
        statement = registry.get("statement") or registry.get("informal_statement", "")
        if statement:
            sections.append(f"Statement: {statement}")
        status = registry.get("status", "unknown")
        sections.append(f"Status: {status}")

    if triage:
        sections.append(f"\n## Triage")
        sections.append(f"Tier: {triage.get('tier', 'unknown')}")
        sections.append(f"Amenability score: {triage.get('amenability_score', 'N/A')}")
        approach = triage.get("approach", "")
        if approach:
            sections.append(f"Recommended approach: {approach}")

    if context.get("problem_description"):
        desc = context["problem_description"]
        # Truncate to keep prompt manageable
        if len(desc) > 2000:
            desc = desc[:2000] + "\n[... truncated]"
        sections.append(f"\n## Problem Description (from README)\n{desc}")

    if context.get("proof_obligations"):
        sections.append(f"\n## Proof Obligations\n{context['proof_obligations'][:1500]}")

    if stage == "prove" and context.get("statement_spec"):
        sections.append(f"\n## Statement Specification\n{context['statement_spec'][:1500]}")

    if benchmark:
        sections.append("\n## External Benchmark Snapshot (Einstein Arena)")
        sections.append(f"Objective: {benchmark.get('objective', 'unknown')}")
        sections.append(f"Current snapshot result: {benchmark.get('our_result', 'n/a')}")
        sections.append(f"Previous public best: {benchmark.get('previous_best', 'n/a')}")
        sections.append(f"Reported improvement: {benchmark.get('improvement', 'n/a')}")
        source_problem = benchmark.get("source_problem_path")
        if source_problem:
            sections.append(f"Source problem key: {source_problem}")

    if workflow:
        sections.append(f"\n## Current Workflow State")
        sections.append(f"Stage: {workflow.get('current_stage', 'unknown')}")
        sections.append(f"Owner: {workflow.get('current_owner', 'unknown')}")
        sections.append(f"Route: {workflow.get('active_route', 'unknown')}")

    if prior_runs:
        sections.append(f"\n## Prior Run Summaries (last {len(prior_runs)})")
        for run in prior_runs:
            run_id = run.get("run_id", "?")
            status = run.get("status", "?")
            verdict = run.get("verdict", "?")
            sections.append(f"- Run {run_id}: status={status}, verdict={verdict}")
            notes = run.get("notes")
            if notes:
                sections.append(f"  Notes: {notes[:200]}")

    # Stage-specific instructions
    stage_instructions: dict[str, str] = {
        "brief": "Create a research brief: scope, objectives, success criteria, compute budget estimate, and risk assessment.",
        "novelty": "Search literature for prior work on this problem. Identify known results, partial progress, and gaps. Produce a bibliography and prior-work memo.",
        "plan": "Create a detailed method plan: algorithm choice, parameter ranges, verification strategy, and expected outputs.",
        "experiment": "Design and describe the computational experiment. Specify: algorithm, parameters, stopping criteria, expected output format, and verification steps.",
        "prove": (
            "Outline and execute a proof strategy that is strictly aligned with statement_spec.md. "
            "Identify key lemmas, required formalizations, potential Lean 4 tactics, and verification checkpoints. "
            "Do not broaden assumptions beyond statement_spec.md."
        ),
        "survey": "Analyze the problem landscape: related problems, structural connections, and promising research directions.",
        "results": "Summarize experimental results: findings, evidence quality, statistical significance where applicable, and next steps.",
        "paper": "Draft a concise research note: abstract, introduction, methods, results, discussion. Use LaTeX for mathematics.",
        "referee": "Review the draft: verify claims against evidence, check reproducibility, identify weaknesses, and assess novelty. Provide a structured referee report.",
    }

    instruction = stage_instructions.get(stage, f"Execute the '{stage}' stage of research.")
    sections.append(f"\n## Task\n{instruction}")

    if benchmark and stage in {"plan", "experiment", "results", "referee"}:
        sections.append(
            "\n## Benchmark Alignment Requirement\n"
            "Explicitly compare your proposed method/results to the benchmark snapshot above "
            "and state whether the output is expected to improve, match, or regress the tracked objective."
        )

    if extra_instructions:
        sections.append(f"\n## Additional Instructions\n{extra_instructions}")

    sections.append(f"\n## Output Format\nProvide your analysis, then include a ```yaml block at the end with structured output containing:")
    sections.append(f"- artifact_type: the type of artifact produced")
    sections.append(f"- evidence_class: R0|R1|E1|E2|H")
    sections.append(f"- confidence: C1|C2|C3")
    sections.append(f"- summary: one-paragraph summary of the output")
    sections.append(f"- key_findings: list of key findings or decisions")

    return "\n".join(sections)


def infer_backend_name(model: str) -> str:
    """Infer backend for explicit model selections."""
    model_lower = model.lower()
    if "claude" in model_lower:
        return "anthropic"
    if "deepseek" in model_lower:
        return "ollama" if ":" in model_lower else "deepseek"
    if any(token in model_lower for token in ("gpt", "o3", "o1")):
        return "openai"
    if any(token in model_lower for token in ("ollama", "llama", "qwen", "mistral")):
        return "ollama"
    if "lmstudio" in model_lower:
        return "lmstudio"
    return "openai"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def ensure_stage_workspace_contract(
    problem_id: str,
    stage: str,
    *,
    dry_run: bool,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Ensure stage prerequisites for workspace/document surfaces.

    For stages beyond brief, a workspace must exist. Required documentation files are
    auto-materialized from minimal templates when missing.
    """
    workspace = REPO_ROOT / "research" / "active" / problem_id
    if stage not in STAGES_REQUIRING_WORKSPACE:
        return {
            "ok": True,
            "workspace_required": False,
            "workspace_path": str(workspace),
            "created_files": [],
        }

    if not workspace.exists() or not workspace.is_dir():
        return {
            "ok": False,
            "workspace_required": True,
            "workspace_path": str(workspace),
            "created_files": [],
            "error": (
                f"Stage '{stage}' requires an initialized workspace at {workspace}. "
                f"Run scaffold and workflow triage before dispatching this stage."
            ),
        }

    required = set(BASE_REQUIRED_WORKSPACE_FILES)
    required.update(STAGE_REQUIRED_WORKSPACE_FILES.get(stage, set()))

    created: list[str] = []
    registry = (context or {}).get("registry") or {}
    triage = (context or {}).get("triage") or {}
    problem_title = str(registry.get("title") or problem_id)
    problem_statement = str(registry.get("statement") or registry.get("informal_statement") or "")
    problem_tier = str(triage.get("tier") or "TBD")

    for relative_path in sorted(required):
        target = workspace / relative_path
        if target.exists():
            if target.is_dir():
                return {
                    "ok": False,
                    "workspace_required": True,
                    "workspace_path": str(workspace),
                    "created_files": created,
                    "error": f"Required file path '{target}' exists as a directory.",
                }
            continue

        created.append(relative_path)
        if dry_run:
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        template = WORKSPACE_FILE_TEMPLATES.get(relative_path, f"# {Path(relative_path).name}\n")
        if relative_path == "README.md":
            template = f"# {problem_title}\n\nRegistry ID: `{problem_id}`\n\nStatus: active\n"
        elif relative_path == "input_files/data_description.md":
            template = (
                f"# Problem Brief\n\n"
                f"- Registry ID: {problem_id}\n"
                f"- Title: {problem_title}\n"
                f"- Tier: {problem_tier}\n"
                f"- Route: experiment-first | proof-first | survey-first\n\n"
                f"## Problem Statement\n\n{problem_statement}\n\n"
                "## Success Condition\n\n"
                "## Stop Conditions\n"
            )
        target.write_text(template, encoding="utf-8")

    return {
        "ok": True,
        "workspace_required": True,
        "workspace_path": str(workspace),
        "created_files": created,
    }


def build_prompt_packet(
    *,
    problem_id: str,
    role: str,
    stage: str,
    messages: list[dict[str, str]],
    requested_model: str,
    resolved_model: str,
    backend: str,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    """Build a reproducibility packet for the exact prompt and routing configuration."""
    return {
        "version": "1.0",
        "problem_id": problem_id,
        "role": role,
        "stage": stage,
        "request": {
            "requested_model": requested_model,
            "resolved_model": resolved_model,
            "backend": backend,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        "messages": messages,
    }


# ──────────────────────────── LLM API Invocation ──────────────────────────────

def _invoke_openai_compatible(
    messages: list[dict[str, str]],
    *,
    model: str,
    base_url: str | None = None,
    api_key: str | None = None,
    max_tokens: int = 4000,
    temperature: float = 0.3,
) -> dict[str, Any]:
    """Call an OpenAI-compatible API (OpenAI, DeepSeek, local servers)."""
    import urllib.request

    url = (base_url or "https://api.openai.com/v1") + "/chat/completions"
    key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY", "")

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    start = time.monotonic()
    with urllib.request.urlopen(req, timeout=300) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    duration = time.monotonic() - start

    content = result["choices"][0]["message"]["content"]
    usage = result.get("usage", {})

    return {
        "content": content,
        "model": result.get("model", model),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "duration_seconds": round(duration, 2),
    }


def _invoke_anthropic(
    messages: list[dict[str, str]],
    *,
    model: str = "claude-sonnet-4-20250514",
    api_key: str | None = None,
    max_tokens: int = 4000,
    temperature: float = 0.3,
) -> dict[str, Any]:
    """Call the Anthropic Claude API."""
    import urllib.request

    url = "https://api.anthropic.com/v1/messages"
    key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")

    # Convert from OpenAI format to Anthropic format
    system_msg = ""
    user_messages = []
    for msg in messages:
        if msg["role"] == "system":
            system_msg = msg["content"]
        else:
            user_messages.append(msg)

    payload: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": user_messages,
    }
    if system_msg:
        payload["system"] = system_msg

    headers = {
        "Content-Type": "application/json",
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    start = time.monotonic()
    with urllib.request.urlopen(req, timeout=300) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    duration = time.monotonic() - start

    content = result["content"][0]["text"]
    usage = result.get("usage", {})

    return {
        "content": content,
        "model": result.get("model", model),
        "prompt_tokens": usage.get("input_tokens", 0),
        "completion_tokens": usage.get("output_tokens", 0),
        "duration_seconds": round(duration, 2),
    }


def invoke_llm(
    messages: list[dict[str, str]],
    *,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 4000,
    temperature: float = DEFAULT_TEMPERATURE,
) -> dict[str, Any]:
    """Route to the appropriate LLM API based on model name / env vars."""
    model_lower = model.lower()

    # Anthropic Claude models
    if "claude" in model_lower:
        return _invoke_anthropic(
            messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    # DeepSeek models
    if "deepseek" in model_lower:
        base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        return _invoke_openai_compatible(
            messages,
            model=model,
            base_url=base_url,
            api_key=api_key,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    # Local models (LM Studio, Ollama, vLLM)
    if any(x in model_lower for x in ("local", "lmstudio", "ollama")):
        base_url = os.environ.get("LOCAL_LLM_URL", "http://localhost:1234/v1")
        return _invoke_openai_compatible(
            messages,
            model=model,
            base_url=base_url,
            api_key="not-needed",
            max_tokens=max_tokens,
            temperature=temperature,
        )

    # Default: OpenAI-compatible
    return _invoke_openai_compatible(
        messages,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )


# ──────────────────────────── Artifact Parsing ────────────────────────────────

def extract_yaml_block(text: str) -> dict[str, Any] | None:
    """Extract the last ```yaml ... ``` block from LLM output."""
    import re
    blocks = re.findall(r"```yaml\s*\n(.*?)```", text, re.DOTALL)
    if not blocks:
        return None
    try:
        return yaml.safe_load(blocks[-1])
    except yaml.YAMLError:
        return None


def save_artifact(
    problem_id: str,
    stage: str,
    content: str,
    metadata: dict[str, Any],
    *,
    prompt_packet: dict[str, Any] | None = None,
) -> Path:
    """Save an artifact to the problem workspace."""
    workspace = REPO_ROOT / "research" / "active" / problem_id
    artifacts_dir = workspace / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{stage}_{timestamp}.md"
    artifact_path = artifacts_dir / filename

    prompt_packet_path: Path | None = None
    prompt_packet_file_sha256: str | None = None
    if prompt_packet is not None:
        prompt_dir = artifacts_dir / "prompts"
        prompt_dir.mkdir(parents=True, exist_ok=True)
        prompt_filename = f"{stage}_{timestamp}.prompt.json"
        prompt_packet_path = prompt_dir / prompt_filename
        prompt_packet_payload = json.dumps(prompt_packet, ensure_ascii=False, indent=2, sort_keys=True)
        prompt_packet_path.write_text(prompt_packet_payload, encoding="utf-8")
        prompt_packet_file_sha256 = _sha256_text(prompt_packet_payload)

    # Build artifact file with metadata header
    header = yaml.safe_dump(
        {
            "stage": stage,
            "created": timestamp,
            "problem_id": problem_id,
            **metadata,
        },
        sort_keys=False,
        allow_unicode=True,
    )

    artifact_content = f"---\n{header}---\n\n{content}"
    artifact_path.write_text(artifact_content, encoding="utf-8")

    # Compute checksum
    checksum = hashlib.sha256(artifact_content.encode("utf-8")).hexdigest()

    # Update artifact manifest
    manifest_path = artifacts_dir / "manifest.yaml"
    manifest: dict[str, Any] = {}
    if manifest_path.exists():
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}

    entries = manifest.setdefault("artifacts", [])
    entry: dict[str, Any] = {
        "path": filename,
        "stage": stage,
        "created": timestamp,
        "checksum_sha256": checksum,
        "evidence_class": metadata.get("evidence_class", "E2"),
        "confidence": metadata.get("confidence", "C2"),
    }
    if prompt_packet_path is not None:
        entry["prompt_packet_path"] = str(prompt_packet_path.relative_to(artifacts_dir)).replace("\\", "/")
    if metadata.get("prompt_packet_sha256"):
        entry["prompt_packet_sha256"] = metadata.get("prompt_packet_sha256")
    if prompt_packet_file_sha256 is not None:
        entry["prompt_packet_file_sha256"] = prompt_packet_file_sha256
    entries.append(entry)
    manifest["last_updated"] = timestamp
    manifest_path.write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    return artifact_path


# ──────────────────────────── Orchestration Engine ────────────────────────────

def dispatch_agent(
    problem_id: str,
    *,
    role: str,
    stage: str,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    prefer_local: bool = False,
    extra_instructions: str = "",
    dry_run: bool = False,
) -> dict[str, Any]:
    """Dispatch a single agent role for a problem stage.

    Returns:
        dict with keys: success, role, stage, artifact_path, llm_response, metadata
    """
    # Load agent definition
    agent_def = load_agent_definition(role)

    # Load problem context
    context = load_problem_context(problem_id)

    workspace_contract = ensure_stage_workspace_contract(problem_id, stage, dry_run=dry_run, context=context)
    if not workspace_contract.get("ok"):
        return {
            "success": False,
            "role": role,
            "stage": stage,
            "error": workspace_contract.get("error", "Workspace contract check failed"),
            "workspace_contract": workspace_contract,
        }

    # Build prompts
    system_prompt = build_system_prompt(agent_def)
    user_prompt = build_user_prompt(stage, context, extra_instructions=extra_instructions)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # Invoke LLM — use model router for profile-based routing when model is default
    resolved_model = model
    resolved_temp = temperature
    max_tokens = ROLE_TOKEN_BUDGET.get(role, 4000)
    resolved_backend = infer_backend_name(model)

    if model == DEFAULT_MODEL:
        triage = context.get("triage") or {}
        tier = triage.get("tier", "default")
        profile, backend = resolve_with_fallback(role, tier, prefer_local=prefer_local)
        resolved_model = profile.model
        resolved_temp = profile.temperature
        max_tokens = profile.max_tokens
        resolved_backend = backend.name

    prompt_packet = build_prompt_packet(
        problem_id=problem_id,
        role=role,
        stage=stage,
        messages=messages,
        requested_model=model,
        resolved_model=resolved_model,
        backend=resolved_backend,
        temperature=resolved_temp,
        max_tokens=max_tokens,
    )
    prompt_packet_sha256 = _sha256_text(_canonical_json(prompt_packet))

    if dry_run:
        return {
            "success": True,
            "role": role,
            "stage": stage,
            "dry_run": True,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "messages": messages,
            "workspace_contract": workspace_contract,
            "prompt_packet_sha256": prompt_packet_sha256,
            "resolved_model": resolved_model,
            "resolved_backend": resolved_backend,
            "resolved_temperature": resolved_temp,
            "resolved_max_tokens": max_tokens,
            "prefer_local": prefer_local,
        }

    llm_result = invoke_llm(
        messages,
        model=resolved_model,
        max_tokens=max_tokens,
        temperature=resolved_temp,
    )

    content = llm_result["content"]

    # Extract structured metadata from YAML block
    yaml_meta = extract_yaml_block(content) or {}

    metadata = {
        "role": role,
        "model_requested": model,
        "model_resolved": resolved_model,
        "model_response": llm_result.get("model", model),
        "backend": resolved_backend,
        "temperature": resolved_temp,
        "max_tokens": max_tokens,
        "evidence_class": yaml_meta.get("evidence_class", "E2"),
        "confidence": yaml_meta.get("confidence", "C2"),
        "prompt_tokens": llm_result.get("prompt_tokens", 0),
        "completion_tokens": llm_result.get("completion_tokens", 0),
        "duration_seconds": llm_result.get("duration_seconds", 0),
        "prompt_packet_sha256": prompt_packet_sha256,
        "workspace_autocreated_files": workspace_contract.get("created_files", []),
        "prefer_local": prefer_local,
    }

    # Save artifact
    artifact_path = save_artifact(problem_id, stage, content, metadata, prompt_packet=prompt_packet)

    return {
        "success": True,
        "role": role,
        "stage": stage,
        "artifact_path": str(artifact_path),
        "metadata": metadata,
        "yaml_block": yaml_meta,
        "content_length": len(content),
        "workspace_contract": workspace_contract,
    }


def run_stage(
    problem_id: str,
    *,
    stage: str,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    prefer_local: bool = False,
    extra_instructions: str = "",
    dry_run: bool = False,
) -> dict[str, Any]:
    """Run a specific workflow stage for a problem.

    Resolves the appropriate agent role from STAGE_TO_ROLE mapping,
    dispatches the agent, and returns the result.
    """
    role = STAGE_TO_ROLE.get(stage)
    if not role:
        return {
            "success": False,
            "error": f"Unknown stage: {stage}. Valid stages: {sorted(STAGE_TO_ROLE.keys())}",
        }

    return dispatch_agent(
        problem_id,
        role=role,
        stage=stage,
        model=model,
        temperature=temperature,
        prefer_local=prefer_local,
        extra_instructions=extra_instructions,
        dry_run=dry_run,
    )


def run_pipeline(
    problem_id: str,
    *,
    from_stage: str,
    to_stage: str,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    prefer_local: bool = False,
    dual_lane: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Run a sequence of stages from from_stage to to_stage.

    Advances the workflow state machine between stages.
    """
    all_stages = list(DEFAULT_PIPELINE_STAGES)
    # Handle route defaults and explicit dual-lane execution.
    context = load_problem_context(problem_id)
    triage = context.get("triage") or {}
    tier = triage.get("tier", "T3-pattern")

    if dual_lane:
        all_stages = list(DUAL_LANE_PIPELINE_STAGES)
    elif tier in ("T4-structural", "T5-foundational"):
        all_stages = list(PROOF_FIRST_PIPELINE_STAGES)

    try:
        start_idx = all_stages.index(from_stage)
    except ValueError:
        return {"success": False, "error": f"Unknown from_stage: {from_stage}"}

    try:
        end_idx = all_stages.index(to_stage)
    except ValueError:
        return {"success": False, "error": f"Unknown to_stage: {to_stage}"}

    if start_idx > end_idx:
        return {"success": False, "error": f"from_stage ({from_stage}) must be before to_stage ({to_stage})"}

    stages_to_run = all_stages[start_idx : end_idx + 1]

    results: list[dict[str, Any]] = []
    for stage in stages_to_run:
        result = run_stage(
            problem_id,
            stage=stage,
            model=model,
            temperature=temperature,
            prefer_local=prefer_local,
            dry_run=dry_run,
        )
        results.append(result)

        if not result.get("success"):
            return {
                "success": False,
                "error": f"Pipeline failed at stage '{stage}'",
                "stage_results": results,
            }

    return {
        "success": True,
        "stages_run": stages_to_run,
        "dual_lane": dual_lane,
        "stage_results": results,
    }


# ──────────────────────────── CLI ─────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="omega-orchestrate",
        description="OMEGA Agent Orchestrator — dispatch LLM-backed research agents.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # run: single stage
    run_parser = sub.add_parser("run", help="Run a single workflow stage")
    run_parser.add_argument("problem_id", help="Problem ID from registry")
    run_parser.add_argument("--stage", required=True, help="Workflow stage to execute")
    run_parser.add_argument("--model", default=DEFAULT_MODEL, help="LLM model name")
    run_parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    run_parser.add_argument("--prefer-local", action="store_true", help="Prefer local model profiles when available")
    run_parser.add_argument("--extra", default="", help="Extra instructions for the agent")
    run_parser.add_argument("--dry-run", action="store_true", help="Print prompts without calling LLM")

    # dispatch: specific role
    dispatch_parser = sub.add_parser("dispatch", help="Dispatch a specific agent role")
    dispatch_parser.add_argument("problem_id", help="Problem ID")
    dispatch_parser.add_argument("--role", required=True, help="Agent role to dispatch")
    dispatch_parser.add_argument("--stage", default="experiment", help="Stage context")
    dispatch_parser.add_argument("--model", default=DEFAULT_MODEL)
    dispatch_parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    dispatch_parser.add_argument("--prefer-local", action="store_true", help="Prefer local model profiles when available")
    dispatch_parser.add_argument("--dry-run", action="store_true")

    # pipeline: multi-stage
    pipe_parser = sub.add_parser("pipeline", help="Run a multi-stage pipeline")
    pipe_parser.add_argument("problem_id", help="Problem ID")
    pipe_parser.add_argument("--from-stage", required=True, help="Start stage")
    pipe_parser.add_argument("--to-stage", required=True, help="End stage (inclusive)")
    pipe_parser.add_argument("--model", default=DEFAULT_MODEL)
    pipe_parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    pipe_parser.add_argument("--prefer-local", action="store_true", help="Prefer local model profiles when available")
    pipe_parser.add_argument("--dual-lane", action="store_true", help="Run both informal (experiment) and formal (prove) lanes in one pipeline")
    pipe_parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if args.command == "run":
        result = run_stage(
            args.problem_id,
            stage=args.stage,
            model=args.model,
            temperature=args.temperature,
            prefer_local=args.prefer_local,
            extra_instructions=args.extra,
            dry_run=args.dry_run,
        )
    elif args.command == "dispatch":
        result = dispatch_agent(
            args.problem_id,
            role=args.role,
            stage=args.stage,
            model=args.model,
            temperature=args.temperature,
            prefer_local=args.prefer_local,
            dry_run=args.dry_run,
        )
    elif args.command == "pipeline":
        result = run_pipeline(
            args.problem_id,
            from_stage=args.from_stage,
            to_stage=args.to_stage,
            model=args.model,
            temperature=args.temperature,
            prefer_local=args.prefer_local,
            dual_lane=args.dual_lane,
            dry_run=args.dry_run,
        )
    else:
        parser.error(f"Unknown command: {args.command}")
        return

    print(yaml.safe_dump(result, sort_keys=False, allow_unicode=True))


if __name__ == "__main__":
    main()
