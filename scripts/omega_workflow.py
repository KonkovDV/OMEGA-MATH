#!/usr/bin/env python3
"""OMEGA deterministic workflow controller for active research workspaces.

Usage:
  python scripts/omega_workflow.py triage <problem-id>
  python scripts/omega_workflow.py status <problem-id>
  python scripts/omega_workflow.py advance <problem-id> --outcome complete
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from omega_runner import REPO_ROOT, VALID_ROUTES, get_problem_root, utc_now_iso

VALID_OUTCOMES = {"complete", "block", "resume", "close"}
EXECUTION_STAGE_BY_ROUTE = {
    "experiment-first": "experiment",
    "proof-first": "prove",
    "survey-first": "survey",
}
ROLE_TO_ROUTE = {
    "experimentalist": "experiment-first",
    "prover": "proof-first",
    "analyst": "survey-first",
    "librarian": "survey-first",
}
FALLBACK_TIER_ROLES = {
    "T1-computational": "experimentalist",
    "T2-experimental": "experimentalist",
    "T3-pattern": "analyst",
    "T4-structural": "prover",
    "T5-foundational": "librarian",
}
TIER_KEY_TO_LABEL = {
    "tier_1_computational": "T1-computational",
    "tier_2_experimental": "T2-experimental",
    "tier_3_pattern": "T3-pattern",
    "tier_4_structural": "T4-structural",
    "tier_5_foundational": "T5-foundational",
}


def workflow_state_path(problem_root: Path) -> Path:
    return problem_root / "control" / "workflow-state.yaml"


def load_yaml_file(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_team_routing(repo_root: Path) -> dict[str, str]:
    team_path = repo_root / "agents" / "team.yaml"
    if not team_path.exists():
        return dict(FALLBACK_TIER_ROLES)
    data = load_yaml_file(team_path) or {}
    orchestration = data.get("orchestration") or {}
    routing_rules = orchestration.get("routing_rules") or {}
    if not isinstance(routing_rules, dict):
        return dict(FALLBACK_TIER_ROLES)
    return {str(key): str(value) for key, value in routing_rules.items()}


def read_workspace_title(problem_root: Path, fallback: str) -> str:
    readme_path = problem_root / "README.md"
    if not readme_path.exists():
        return fallback
    for line in readme_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            return title or fallback
    return fallback


def iter_queue_entries(repo_root: Path) -> list[dict[str, Any]]:
    triage_path = repo_root / "registry" / "triage-matrix.yaml"
    if not triage_path.exists():
        return []
    payload = load_yaml_file(triage_path) or {}
    if not isinstance(payload, dict):
        return []
    entries: list[dict[str, Any]] = []
    for key, value in payload.items():
        if not isinstance(value, list):
            continue
        tier = TIER_KEY_TO_LABEL.get(str(key))
        for item in value:
            if not isinstance(item, dict):
                continue
            enriched = dict(item)
            if tier is not None and "tier" not in enriched:
                enriched["tier"] = tier
            entries.append(enriched)
    return entries


def find_queue_entry(repo_root: Path, problem_id: str) -> dict[str, Any] | None:
    for entry in iter_queue_entries(repo_root):
        if entry.get("id") == problem_id:
            return entry
    return None


def find_problem_record(repo_root: Path, problem_id: str) -> dict[str, Any] | None:
    domains_dir = repo_root / "registry" / "domains"
    if not domains_dir.exists():
        return None
    for domain_file in sorted(domains_dir.glob("*.yaml")):
        data = load_yaml_file(domain_file) or {}
        problems = data.get("problems") or []
        if not isinstance(problems, list):
            continue
        for problem in problems:
            if isinstance(problem, dict) and problem.get("id") == problem_id:
                record = dict(problem)
                record.setdefault("domain", domain_file.stem)
                return record
    return None


def select_execution_role(tier: str | None, repo_root: Path) -> str:
    if tier is None:
        return "librarian"
    routing = load_team_routing(repo_root)
    return routing.get(tier, FALLBACK_TIER_ROLES.get(tier, "librarian"))


def select_route(execution_role: str, route_override: str | None = None) -> str:
    if route_override is not None:
        if route_override not in VALID_ROUTES:
            raise ValueError(f"Route must be one of {sorted(VALID_ROUTES)}; got {route_override}")
        return route_override
    return ROLE_TO_ROUTE.get(execution_role, "survey-first")


def execution_role_for_route(route: str, current_role: str | None = None) -> str:
    if route == "experiment-first":
        return "experimentalist"
    if route == "proof-first":
        return "prover"
    if current_role in {"analyst", "librarian"}:
        return current_role
    return "librarian"


def build_stage_sequence(route: str) -> list[str]:
    execution_stage = EXECUTION_STAGE_BY_ROUTE[route]
    return ["brief", "novelty", "triage", "plan", execution_stage, "results", "paper", "referee", "closed"]


def _append_history(
    state: dict[str, Any],
    *,
    event: str,
    from_stage: str | None,
    to_stage: str,
    notes: str,
    timestamp: str,
) -> None:
    history = state.setdefault("history", [])
    history.append(
        {
            "at": timestamp,
            "event": event,
            "from_stage": from_stage,
            "to_stage": to_stage,
            "notes": notes,
        }
    )


def _set_stage(
    state: dict[str, Any],
    *,
    route: str,
    execution_role: str,
    stage: str,
    stage_status: str,
) -> None:
    state["current_stage"] = stage
    state["current_owner"] = owner_for_stage(route, stage, execution_role)
    state["stage_status"] = stage_status


def owner_for_stage(route: str, stage: str, execution_role: str) -> str:
    if stage == "survey":
        return execution_role if execution_role in {"analyst", "librarian"} else "librarian"
    if stage == "results":
        if route == "experiment-first":
            return "experimentalist"
        if route == "proof-first":
            return "prover"
        return execution_role if execution_role in {"analyst", "librarian"} else "analyst"
    return {
        "brief": "planner",
        "novelty": "librarian",
        "triage": "analyst",
        "plan": "planner",
        "experiment": "experimentalist",
        "prove": "prover",
        "paper": "writer",
        "referee": "reviewer",
        "closed": "planner",
    }[stage]


def build_triage_metadata(repo_root: Path, problem_id: str, route_override: str | None = None) -> dict[str, Any]:
    queue_entry = find_queue_entry(repo_root, problem_id)
    record = find_problem_record(repo_root, problem_id)

    tier = None
    score = None
    triage_source = None

    if record is not None:
        ai_triage = record.get("ai_triage") or {}
        if isinstance(ai_triage, dict) and ai_triage.get("tier"):
            tier = str(ai_triage.get("tier"))
            score = ai_triage.get("amenability_score")
            triage_source = "canonical-record"

    if tier is None and queue_entry is not None:
        if queue_entry.get("tier"):
            tier = str(queue_entry.get("tier"))
        if queue_entry.get("score") is not None:
            score = queue_entry.get("score")
        triage_source = "triage-matrix"

    execution_role = select_execution_role(tier, repo_root)
    recommended_route = select_route(execution_role)
    active_route = select_route(execution_role, route_override)

    if tier is None:
        tier = "untriaged"
        triage_source = "default-untriaged"
        execution_role = "librarian"
        recommended_route = "survey-first"
        active_route = select_route(execution_role, route_override)

    title = problem_id
    domain = None
    if record is not None:
        title = str(record.get("name") or title)
        domain = record.get("domain")
    elif queue_entry is not None:
        title = str(queue_entry.get("name") or title)
        domain = queue_entry.get("domain")

    return {
        "problem_id": problem_id,
        "title": title,
        "domain": domain,
        "tier": tier,
        "amenability_score": score,
        "triage_source": triage_source,
        "execution_role": execution_role,
        "recommended_route": recommended_route,
        "active_route": active_route,
        "approach": queue_entry.get("approach") if queue_entry else None,
        "compute": queue_entry.get("compute") if queue_entry else None,
        "routing_reason": (
            f"manual override -> {active_route}" if route_override is not None else f"tier {tier} -> {execution_role} -> {active_route}"
        ),
    }


def write_workflow_state(path: Path, state: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(state, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


def load_workflow_state(repo_root: Path, problem_id: str) -> dict[str, Any]:
    problem_root = get_problem_root(repo_root, problem_id)
    path = workflow_state_path(problem_root)
    if not path.exists():
        raise FileNotFoundError(
            f"Workflow state not found: {path}. Run python scripts/omega-workflow.py triage {problem_id} first."
        )
    data = load_yaml_file(path)
    if not isinstance(data, dict):
        raise ValueError(f"Workflow state must be a YAML mapping: {path}")
    return data


def initialize_workflow_state(
    repo_root: Path,
    problem_id: str,
    *,
    route_override: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    problem_root = get_problem_root(repo_root, problem_id)
    metadata = build_triage_metadata(repo_root, problem_id, route_override=route_override)
    metadata["title"] = read_workspace_title(problem_root, str(metadata["title"]))
    stages = build_stage_sequence(str(metadata["active_route"]))
    state_path = workflow_state_path(problem_root)
    if state_path.exists() and not force:
        raise FileExistsError(f"{state_path} already exists; pass --force to overwrite")

    timestamp = utc_now_iso()
    state = {
        "version": "1.0",
        "problem_id": problem_id,
        "title": metadata["title"],
        "domain": metadata["domain"],
        "tier": metadata["tier"],
        "amenability_score": metadata["amenability_score"],
        "triage_source": metadata["triage_source"],
        "approach": metadata["approach"],
        "compute": metadata["compute"],
        "controller": "planner",
        "execution_role": metadata["execution_role"],
        "recommended_route": metadata["recommended_route"],
        "active_route": metadata["active_route"],
        "current_stage": stages[0],
        "current_owner": owner_for_stage(str(metadata["active_route"]), stages[0], str(metadata["execution_role"])),
        "stage_status": "ready",
        "active_run_id": None,
        "active_run_status": None,
        "active_run_agent": None,
        "last_run_id": None,
        "last_run_status": None,
        "last_verdict": None,
        "last_proof_result_path": None,
        "last_proof_status": None,
        "stages": stages,
        "last_updated": timestamp,
        "history": [
            {
                "at": timestamp,
                "event": "triaged",
                "from_stage": None,
                "to_stage": stages[0],
                "notes": metadata["routing_reason"],
            }
        ],
    }
    write_workflow_state(state_path, state)
    return state


def switch_workflow_route(state: dict[str, Any], *, route: str) -> bool:
    if route not in VALID_ROUTES:
        raise ValueError(f"Route must be one of {sorted(VALID_ROUTES)}; got {route}")

    current_route = str(state.get("active_route") or route)
    if current_route == route:
        return False

    previous_stage = str(state.get("current_stage") or build_stage_sequence(route)[0])
    execution_role = execution_role_for_route(route, str(state.get("execution_role") or ""))
    stages = build_stage_sequence(route)
    next_stage = previous_stage if previous_stage in stages else EXECUTION_STAGE_BY_ROUTE[route]
    timestamp = utc_now_iso()

    state["active_route"] = route
    state["execution_role"] = execution_role
    state["stages"] = stages
    state["current_stage"] = next_stage
    state["current_owner"] = owner_for_stage(route, next_stage, execution_role)
    state["last_updated"] = timestamp
    _append_history(
        state,
        event="route-switched",
        from_stage=previous_stage,
        to_stage=next_stage,
        notes=f"{current_route} -> {route}",
        timestamp=timestamp,
    )
    return True


def ensure_workflow_state(
    repo_root: Path,
    problem_id: str,
    *,
    route_override: str | None = None,
) -> dict[str, Any]:
    problem_root = get_problem_root(repo_root, problem_id)
    try:
        state = load_workflow_state(repo_root, problem_id)
    except FileNotFoundError:
        return initialize_workflow_state(repo_root, problem_id, route_override=route_override)

    if route_override is not None and switch_workflow_route(state, route=route_override):
        write_workflow_state(workflow_state_path(problem_root), state)
    return state


def sync_workflow_for_run_start(
    repo_root: Path,
    problem_id: str,
    *,
    route: str,
    run_id: str,
    agent: str,
) -> dict[str, Any]:
    state = ensure_workflow_state(repo_root, problem_id, route_override=route)
    problem_root = get_problem_root(repo_root, problem_id)
    execution_role = execution_role_for_route(route, str(state.get("execution_role") or agent))
    execution_stage = EXECUTION_STAGE_BY_ROUTE[route]
    previous_stage = str(state.get("current_stage") or execution_stage)
    timestamp = utc_now_iso()

    state["execution_role"] = execution_role
    state["active_route"] = route
    state["stages"] = build_stage_sequence(route)
    _set_stage(
        state,
        route=route,
        execution_role=execution_role,
        stage=execution_stage,
        stage_status="running",
    )
    state["active_run_id"] = run_id
    state["active_run_status"] = "running"
    state["active_run_agent"] = agent
    state["last_run_id"] = run_id
    state["last_run_status"] = "running"
    state["last_updated"] = timestamp
    _append_history(
        state,
        event="run-started",
        from_stage=previous_stage,
        to_stage=execution_stage,
        notes=f"{agent} -> {route} ({run_id})",
        timestamp=timestamp,
    )
    write_workflow_state(workflow_state_path(problem_root), state)
    return state


def sync_workflow_for_run_finish(
    repo_root: Path,
    problem_id: str,
    *,
    route: str,
    run_id: str,
    status: str,
    verdict: str | None,
) -> dict[str, Any]:
    state = ensure_workflow_state(repo_root, problem_id, route_override=route)
    problem_root = get_problem_root(repo_root, problem_id)
    execution_role = execution_role_for_route(route, str(state.get("execution_role") or ""))
    execution_stage = EXECUTION_STAGE_BY_ROUTE[route]
    previous_stage = str(state.get("current_stage") or execution_stage)
    next_stage = previous_stage
    next_status = str(state.get("stage_status") or "ready")
    timestamp = utc_now_iso()

    if previous_stage != "closed" and (previous_stage == execution_stage or state.get("active_run_id") == run_id or next_status == "running"):
        next_stage = "results"
        next_status = "ready"
        _set_stage(
            state,
            route=route,
            execution_role=execution_role,
            stage=next_stage,
            stage_status=next_status,
        )
    elif previous_stage == "closed":
        next_status = "completed"
        state["stage_status"] = next_status
    else:
        if next_status == "running":
            next_status = "ready"
            state["stage_status"] = next_status

    state["active_run_id"] = None
    state["active_run_status"] = None
    state["active_run_agent"] = None
    state["last_run_id"] = run_id
    state["last_run_status"] = status
    if verdict is not None:
        state["last_verdict"] = verdict
    state["last_updated"] = timestamp
    note = f"{status} ({run_id})" if verdict is None else f"{status} / {verdict} ({run_id})"
    _append_history(
        state,
        event="run-finished",
        from_stage=previous_stage,
        to_stage=next_stage,
        notes=note,
        timestamp=timestamp,
    )
    write_workflow_state(workflow_state_path(problem_root), state)
    return state


def record_proof_result(
    repo_root: Path,
    problem_id: str,
    *,
    run_id: str,
    proof_status: str,
    result_path: str,
    run_status: str | None = None,
) -> dict[str, Any]:
    state = ensure_workflow_state(repo_root, problem_id, route_override="proof-first")
    problem_root = get_problem_root(repo_root, problem_id)
    previous_stage = str(state.get("current_stage") or "prove")
    execution_role = execution_role_for_route("proof-first", str(state.get("execution_role") or "prover"))
    next_stage = previous_stage
    timestamp = utc_now_iso()

    if run_status is not None and run_status != "running" and previous_stage == "prove":
        next_stage = "results"
        _set_stage(
            state,
            route="proof-first",
            execution_role=execution_role,
            stage=next_stage,
            stage_status="ready",
        )

    state["last_proof_result_path"] = result_path
    state["last_proof_status"] = proof_status
    state["last_updated"] = timestamp
    _append_history(
        state,
        event="proof-result-recorded",
        from_stage=previous_stage,
        to_stage=next_stage,
        notes=f"{proof_status} ({run_id}) -> {result_path}",
        timestamp=timestamp,
    )
    write_workflow_state(workflow_state_path(problem_root), state)
    return state


def advance_workflow_state(
    repo_root: Path,
    problem_id: str,
    *,
    outcome: str = "complete",
    notes: str | None = None,
) -> dict[str, Any]:
    if outcome not in VALID_OUTCOMES:
        raise ValueError(f"Outcome must be one of {sorted(VALID_OUTCOMES)}; got {outcome}")

    problem_root = get_problem_root(repo_root, problem_id)
    state = load_workflow_state(repo_root, problem_id)
    current_stage = str(state["current_stage"])
    route = str(state["active_route"])
    execution_role = str(state.get("execution_role") or "librarian")
    stages = [str(stage) for stage in state.get("stages") or []]
    history = state.setdefault("history", [])
    timestamp = utc_now_iso()

    if outcome == "block":
        state["stage_status"] = "blocked"
        history.append({"at": timestamp, "event": "blocked", "from_stage": current_stage, "to_stage": current_stage, "notes": notes or ""})
    elif outcome == "resume":
        state["stage_status"] = "ready"
        history.append({"at": timestamp, "event": "resumed", "from_stage": current_stage, "to_stage": current_stage, "notes": notes or ""})
    elif outcome == "close":
        state["current_stage"] = "closed"
        state["current_owner"] = owner_for_stage(route, "closed", execution_role)
        state["stage_status"] = "completed"
        history.append({"at": timestamp, "event": "closed", "from_stage": current_stage, "to_stage": "closed", "notes": notes or ""})
    else:
        if current_stage == "closed":
            raise ValueError("Workflow is already closed")
        current_index = stages.index(current_stage)
        next_stage = stages[current_index + 1]
        state["current_stage"] = next_stage
        state["current_owner"] = owner_for_stage(route, next_stage, execution_role)
        state["stage_status"] = "completed" if next_stage == "closed" else "ready"
        history.append({"at": timestamp, "event": "completed", "from_stage": current_stage, "to_stage": next_stage, "notes": notes or ""})

    state["last_updated"] = timestamp
    write_workflow_state(workflow_state_path(problem_root), state)
    return state


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OMEGA deterministic workflow controller")
    subparsers = parser.add_subparsers(dest="command", required=True)

    triage_parser = subparsers.add_parser("triage", help="Create or refresh workflow state from registry triage")
    triage_parser.add_argument("problem_id")
    triage_parser.add_argument("--route", choices=sorted(VALID_ROUTES))
    triage_parser.add_argument("--force", action="store_true")

    status_parser = subparsers.add_parser("status", help="Read the current workflow state")
    status_parser.add_argument("problem_id")

    advance_parser = subparsers.add_parser("advance", help="Advance or update the workflow state")
    advance_parser.add_argument("problem_id")
    advance_parser.add_argument("--outcome", default="complete", choices=sorted(VALID_OUTCOMES))
    advance_parser.add_argument("--notes")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "triage":
            state = initialize_workflow_state(REPO_ROOT, args.problem_id, route_override=args.route, force=args.force)
        elif args.command == "status":
            state = load_workflow_state(REPO_ROOT, args.problem_id)
        else:
            state = advance_workflow_state(REPO_ROOT, args.problem_id, outcome=args.outcome, notes=args.notes)
    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1

    print(yaml.safe_dump(state, sort_keys=False, allow_unicode=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())