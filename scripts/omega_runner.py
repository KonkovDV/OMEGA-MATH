#!/usr/bin/env python3
"""OMEGA local runner substrate for active research workspaces.

Usage:
    python scripts/omega_runner.py start <problem-id> --route experiment-first --agent experimentalist --description "..."
    python scripts/omega_runner.py finish <problem-id> <run-id> --status completed --verdict positive --artifact artifacts/log.txt:log
    python scripts/omega_runner.py proof-result <problem-id> <run-id> --claim-label "..." --claim-class theorem --status draft --verifier lean4 --toolchain leanprover/lean4:v4.29.0 --verifier-command "lake env lean ..."
    python scripts/omega_runner.py evidence-bundle <problem-id>
    python scripts/generate_experiment_index.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
VALID_ROUTES = {"experiment-first", "proof-first", "survey-first"}
VALID_RUN_STATUSES = {"running", "completed", "failed", "abandoned"}
VALID_VERDICTS = {"positive", "negative", "inconclusive"}
VALID_PROOF_STATUSES = {
    "draft",
    "verifier-checked",
    "formally-checked",
    "partial",
    "verified",
    "rejected",
    "needs-human-review",
}
VALID_CLAIM_CLASSES = {"lemma", "theorem", "structural-claim", "counterexample-cert"}
VALID_VERIFIER_KINDS = {"lean4", "coq", "isabelle", "cas", "human-line-check"}
VALID_LEDGER_ARTIFACT_TYPES = {
    "log",
    "dataset",
    "proof-draft",
    "prover-result",
    "counterexample",
    "plot",
    "failure-pattern",
    "prompt-packet",
    "synthetic-taxonomy",
    "evaluation-packet",
}
VALID_PROOF_ARTIFACT_TYPES = {"source", "log", "transcript", "proof-term", "report"}
EVIDENCE_BUNDLE_PATH = "artifacts/evidence-bundle.yaml"
FAILURE_CHANNEL_PATH = "control/failure-patterns.jsonl"
EVIDENCE_DOCUMENTS = (
    ("README.md", "landing-page"),
    ("reproducibility.md", "reproducibility-manifest"),
    ("input_files/proof_obligations.md", "proof-obligations"),
)


def ensure_required_evidence_documents(problem_root: Path) -> None:
    missing: list[str] = []
    for relative_path, _role in EVIDENCE_DOCUMENTS:
        normalized, resolved = resolve_workspace_path(problem_root, relative_path)
        if not resolved.exists() or not resolved.is_file():
            missing.append(normalized)
    if missing:
        raise ValueError(
            "Cannot finish completed run: missing required evidence documents: "
            + ", ".join(sorted(missing))
        )


def _read_workspace_heading(problem_root: Path) -> str:
    readme_path = problem_root / "README.md"
    if not readme_path.exists():
        return problem_root.name
    for line in readme_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            return title or problem_root.name
    return problem_root.name


def _load_workflow_summary(problem_root: Path) -> dict[str, object]:
    workflow_path = problem_root / "control" / "workflow-state.yaml"
    if not workflow_path.exists():
        return {
            "workflow_exists": False,
            "title": _read_workspace_heading(problem_root),
            "domain": None,
            "tier": None,
            "amenability_score": None,
            "active_route": None,
            "current_stage": None,
            "current_owner": None,
            "workflow_status": None,
            "execution_role": None,
            "workflow_last_updated": None,
            "active_run_id": None,
            "active_run_status": None,
            "last_run_id": None,
            "last_run_status": None,
            "last_verdict": None,
            "last_proof_result_path": None,
            "last_proof_status": None,
            "blocked": False,
        }

    payload = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Workflow state must contain a YAML mapping: {workflow_path}")

    workflow_status = payload.get("stage_status")
    return {
        "workflow_exists": True,
        "title": payload.get("title") or _read_workspace_heading(problem_root),
        "domain": payload.get("domain"),
        "tier": payload.get("tier"),
        "amenability_score": payload.get("amenability_score"),
        "active_route": payload.get("active_route"),
        "current_stage": payload.get("current_stage"),
        "current_owner": payload.get("current_owner"),
        "workflow_status": workflow_status,
        "execution_role": payload.get("execution_role"),
        "workflow_last_updated": payload.get("last_updated"),
        "active_run_id": payload.get("active_run_id"),
        "active_run_status": payload.get("active_run_status"),
        "last_run_id": payload.get("last_run_id"),
        "last_run_status": payload.get("last_run_status"),
        "last_verdict": payload.get("last_verdict"),
        "last_proof_result_path": payload.get("last_proof_result_path"),
        "last_proof_status": payload.get("last_proof_status"),
        "blocked": workflow_status == "blocked",
    }


def _sync_workflow_start(repo_root: Path, problem_id: str, *, route: str, run_id: str, agent: str) -> None:
    from omega_workflow import sync_workflow_for_run_start

    sync_workflow_for_run_start(repo_root, problem_id, route=route, run_id=run_id, agent=agent)


def _sync_workflow_finish(
    repo_root: Path,
    problem_id: str,
    *,
    route: str,
    run_id: str,
    status: str,
    verdict: str | None,
) -> None:
    from omega_workflow import sync_workflow_for_run_finish

    sync_workflow_for_run_finish(repo_root, problem_id, route=route, run_id=run_id, status=status, verdict=verdict)


def _record_workflow_proof_result(
    repo_root: Path,
    problem_id: str,
    *,
    run_id: str,
    proof_status: str,
    result_path: str,
    run_status: str | None,
) -> None:
    from omega_workflow import record_proof_result

    record_proof_result(
        repo_root,
        problem_id,
        run_id=run_id,
        proof_status=proof_status,
        result_path=result_path,
        run_status=run_status,
    )


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def get_problem_root(repo_root: Path, problem_id: str) -> Path:
    problem_root = repo_root / "research" / "active" / problem_id
    if not problem_root.exists() or not problem_root.is_dir():
        raise FileNotFoundError(
            f"Problem workspace not found: {problem_root}. Run python scripts/scaffold_problem.py {problem_id} --title \"...\" first."
        )
    return problem_root


def ensure_relative_artifact_path(path_value: str) -> str:
    artifact_path = Path(path_value)
    if artifact_path.is_absolute():
        raise ValueError(f"Artifact path must be relative to the problem workspace: {path_value}")
    if any(part == ".." for part in artifact_path.parts):
        raise ValueError(f"Artifact path may not escape the problem workspace: {path_value}")
    normalized = artifact_path.as_posix()
    if normalized in {"", "."}:
        raise ValueError("Artifact path may not be empty")
    return normalized


def validate_artifacts(artifacts: list[dict] | None, valid_types: set[str]) -> list[dict]:
    normalized: list[dict] = []
    for artifact in artifacts or []:
        artifact_type = artifact.get("type")
        if artifact_type not in valid_types:
            raise ValueError(f"Artifact type must be one of {sorted(valid_types)}; got {artifact_type}")
        normalized.append(
            {
                "path": ensure_relative_artifact_path(str(artifact.get("path", ""))),
                "type": artifact_type,
                **({"checksum": artifact["checksum"]} if artifact.get("checksum") else {}),
            }
        )
    return normalized


def resolve_workspace_path(problem_root: Path, path_value: str) -> tuple[str, Path]:
    normalized = ensure_relative_artifact_path(path_value)
    return normalized, problem_root / Path(normalized)


def append_workspace_jsonl(problem_root: Path, path_value: str, payload: dict[str, Any]) -> str:
    normalized, resolved = resolve_workspace_path(problem_root, path_value)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(payload, ensure_ascii=False)
    with resolved.open("a", encoding="utf-8") as handle:
        handle.write(f"{line}\n")
    return normalized


def compute_artifact_checksum(artifact_path: Path) -> str:
    digest = hashlib.sha256()
    with artifact_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def describe_workspace_file(
    problem_root: Path,
    path_value: str,
    *,
    expected_checksum: str | None = None,
    label: str = "Artifact",
) -> dict:
    normalized, resolved = resolve_workspace_path(problem_root, path_value)
    if not resolved.exists() or not resolved.is_file():
        raise FileNotFoundError(f"{label} not found: {resolved}")
    checksum = compute_artifact_checksum(resolved)
    if expected_checksum is not None and checksum != expected_checksum:
        raise ValueError(f"{label} checksum mismatch for {normalized}")
    stat = resolved.stat()
    return {
        "path": normalized,
        "checksum": checksum,
        "size_bytes": stat.st_size,
    }


def enrich_artifacts(problem_root: Path, artifacts: list[dict], *, valid_types: set[str]) -> list[dict]:
    enriched: list[dict] = []
    for artifact in artifacts:
        artifact_type = artifact.get("type")
        if artifact_type not in valid_types:
            raise ValueError(f"Artifact type must be one of {sorted(valid_types)}; got {artifact_type}")
        described = describe_workspace_file(
            problem_root,
            str(artifact.get("path", "")),
            expected_checksum=artifact.get("checksum"),
        )
        enriched.append(
            {
                "path": described["path"],
                "type": artifact_type,
                "checksum": described["checksum"],
                "size_bytes": described["size_bytes"],
            }
        )
    return enriched


def ensure_workspace_file_exists(problem_root: Path, path_value: str, *, label: str) -> str:
    described = describe_workspace_file(problem_root, path_value, label=label)
    return described["path"]


def ledger_path(problem_root: Path) -> Path:
    return problem_root / "experiments" / "ledger.yaml"


def read_yaml(path: Path) -> object:
    if not path.exists():
        raise FileNotFoundError(path)
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_ledger(problem_root: Path) -> list[dict]:
    path = ledger_path(problem_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("[]\n", encoding="utf-8")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return []
    if not isinstance(data, list):
        raise ValueError(f"Ledger must contain a YAML list: {path}")
    return data


def write_ledger(problem_root: Path, ledger: list[dict]) -> Path:
    path = ledger_path(problem_root)
    path.write_text(yaml.safe_dump(ledger, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


def allocate_run_id(repo_root: Path, problem_id: str) -> str:
    problem_root = get_problem_root(repo_root, problem_id)
    ledger = load_ledger(problem_root)
    today = datetime.now(UTC).strftime("%Y%m%d")
    prefix = f"{problem_id}-{today}-"
    next_sequence = 1
    for entry in ledger:
        run_id = str(entry.get("run_id", ""))
        if run_id.startswith(prefix):
            try:
                next_sequence = max(next_sequence, int(run_id.rsplit("-", 1)[-1]) + 1)
            except ValueError:
                continue
    return f"{problem_id}-{today}-{next_sequence:03d}"


def bootstrap_lean_starter(repo_root: Path, problem_id: str, *, overwrite: bool = True) -> Path:
    template_root = repo_root / "templates" / "lean-starter"
    if not template_root.exists():
        raise FileNotFoundError(f"Lean starter template not found: {template_root}")
    problem_root = get_problem_root(repo_root, problem_id)
    target_root = problem_root / "proof" / "lean"
    if target_root.exists():
        if not overwrite:
            return target_root
        for child in sorted(target_root.rglob("*"), reverse=True):
            if child.is_file() or child.is_symlink():
                child.unlink()
            elif child.is_dir():
                child.rmdir()
    target_root.mkdir(parents=True, exist_ok=True)
    for source in template_root.rglob("*"):
        relative = source.relative_to(template_root)
        destination = target_root / relative
        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())
    return target_root


def generate_experiment_index(repo_root: Path) -> list[dict]:
    active_root = repo_root / "research" / "active"
    index_entries: list[dict] = []
    for candidate in sorted(active_root.iterdir(), key=lambda item: item.name.lower()):
        if not candidate.is_dir():
            continue
        workflow_summary = _load_workflow_summary(candidate)
        current_ledger_path = candidate / "experiments" / "ledger.yaml"
        ledger: list[dict] = []
        latest: dict | None = None
        if current_ledger_path.exists():
            raw_ledger = yaml.safe_load(current_ledger_path.read_text(encoding="utf-8"))
            if raw_ledger is None:
                ledger = []
            elif isinstance(raw_ledger, list):
                ledger = raw_ledger
            else:
                raise ValueError(f"Experiment ledger must contain a YAML list: {current_ledger_path}")
            if ledger:
                latest = ledger[-1]

        if latest is None and not workflow_summary["workflow_exists"]:
            continue

        latest_artifact_types = sorted(
            {
                str(artifact.get("type"))
                for artifact in ((latest or {}).get("artifacts") or [])
                if artifact.get("type")
            }
        )
        last_updated = workflow_summary["workflow_last_updated"] or (latest or {}).get("finished") or (latest or {}).get("started") or utc_now_iso()
        index_entries.append(
            {
                "problem_id": candidate.name,
                "title": workflow_summary["title"],
                "domain": workflow_summary["domain"],
                "tier": workflow_summary["tier"],
                "amenability_score": workflow_summary["amenability_score"],
                "latest_run": latest.get("run_id") if latest else None,
                "latest_verdict": latest.get("verdict") if latest else workflow_summary["last_verdict"],
                "total_runs": len(ledger),
                "active_route": workflow_summary["active_route"],
                "current_stage": workflow_summary["current_stage"],
                "current_owner": workflow_summary["current_owner"],
                "workflow_status": workflow_summary["workflow_status"],
                "execution_role": workflow_summary["execution_role"],
                "workflow_exists": workflow_summary["workflow_exists"],
                "blocked": workflow_summary["blocked"],
                "active_run_id": workflow_summary["active_run_id"],
                "active_run_status": workflow_summary["active_run_status"],
                "last_run_id": workflow_summary["last_run_id"],
                "last_run_status": workflow_summary["last_run_status"],
                "latest_artifact_types": latest_artifact_types,
                "last_proof_result_path": workflow_summary["last_proof_result_path"],
                "last_proof_status": workflow_summary["last_proof_status"],
                "last_updated": last_updated,
            }
        )
    index_path = active_root / "experiment-index.yaml"
    index_path.write_text(yaml.safe_dump(index_entries, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return index_entries


def generate_evidence_bundle(repo_root: Path, problem_id: str) -> Path:
    problem_root = get_problem_root(repo_root, problem_id)
    ledger = load_ledger(problem_root)
    summary_by_type: dict[str, int] = {}
    total_artifacts = 0
    total_bytes = 0
    runs: list[dict] = []

    for entry in ledger:
        run_artifacts = enrich_artifacts(
            problem_root,
            [
                {
                    "path": artifact.get("path", ""),
                    "type": artifact.get("type"),
                    **({"checksum": artifact["checksum"]} if artifact.get("checksum") else {}),
                }
                for artifact in entry.get("artifacts", [])
            ],
            valid_types=VALID_LEDGER_ARTIFACT_TYPES,
        )
        for artifact in run_artifacts:
            total_artifacts += 1
            total_bytes += artifact["size_bytes"]
            summary_by_type[artifact["type"]] = summary_by_type.get(artifact["type"], 0) + 1
        runs.append(
            {
                "run_id": entry.get("run_id"),
                "route": entry.get("route"),
                "agent": entry.get("agent"),
                "status": entry.get("status"),
                "verdict": entry.get("verdict"),
                "started": entry.get("started"),
                "finished": entry.get("finished"),
                "artifacts": run_artifacts,
            }
        )

    documents = []
    for relative_path, role in EVIDENCE_DOCUMENTS:
        normalized, resolved = resolve_workspace_path(problem_root, relative_path)
        if resolved.exists() and resolved.is_file():
            described = describe_workspace_file(problem_root, normalized, label=role)
            documents.append(
                {
                    "path": described["path"],
                    "role": role,
                    "exists": True,
                    "checksum": described["checksum"],
                    "size_bytes": described["size_bytes"],
                }
            )
        else:
            documents.append({"path": normalized, "role": role, "exists": False})

    required_documents_total = len(EVIDENCE_DOCUMENTS)
    required_documents_present = sum(1 for document in documents if document.get("exists"))
    completeness_score = (
        required_documents_present / required_documents_total if required_documents_total > 0 else 1.0
    )

    payload = {
        "version": "1.0",
        "problem_id": problem_id,
        "generated_at": utc_now_iso(),
        "summary": {
            "total_runs": len(ledger),
            "total_artifacts": total_artifacts,
            "total_bytes": total_bytes,
            "by_type": dict(sorted(summary_by_type.items())),
            "required_documents_total": required_documents_total,
            "required_documents_present": required_documents_present,
            "evidence_completeness_score": completeness_score,
        },
        "documents": documents,
        "runs": runs,
    }

    bundle_relative, bundle_path = resolve_workspace_path(problem_root, EVIDENCE_BUNDLE_PATH)
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    payload["bundle_path"] = bundle_relative
    bundle_path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return bundle_path


def start_run(
    *,
    repo_root: Path,
    problem_id: str,
    route: str,
    agent: str,
    description: str,
    parent_run: str | None = None,
    bound: str | None = None,
    model: str | None = None,
    hardware: str | None = None,
    bootstrap_lean: bool = False,
) -> str:
    if route not in VALID_ROUTES:
        raise ValueError(f"Route must be one of {sorted(VALID_ROUTES)}; got {route}")
    if not agent.strip():
        raise ValueError("Agent is required")
    problem_root = get_problem_root(repo_root, problem_id)
    if bootstrap_lean:
        bootstrap_lean_starter(repo_root, problem_id)
    ledger = load_ledger(problem_root)
    run_id = allocate_run_id(repo_root, problem_id)
    parameters = {"description": description}
    if bound:
        parameters["bound"] = bound
    if model:
        parameters["model"] = model
    if hardware:
        parameters["hardware"] = hardware
    ledger.append(
        {
            "run_id": run_id,
            "problem_id": problem_id,
            "started": utc_now_iso(),
            "finished": None,
            "route": route,
            "agent": agent,
            "status": "running",
            "verdict": None,
            "parameters": parameters,
            "artifacts": [],
            "parent_run": parent_run,
            "notes": "",
        }
    )
    write_ledger(problem_root, ledger)
    _sync_workflow_start(repo_root, problem_id, route=route, run_id=run_id, agent=agent)
    generate_experiment_index(repo_root)
    return run_id


def finish_run(
    *,
    repo_root: Path,
    problem_id: str,
    run_id: str,
    status: str,
    verdict: str | None = None,
    artifacts: list[dict] | None = None,
    notes: str | None = None,
) -> Path:
    if status not in VALID_RUN_STATUSES:
        raise ValueError(f"Run status must be one of {sorted(VALID_RUN_STATUSES)}; got {status}")
    if verdict is not None and verdict not in VALID_VERDICTS:
        raise ValueError(f"Verdict must be one of {sorted(VALID_VERDICTS)}; got {verdict}")
    problem_root = get_problem_root(repo_root, problem_id)
    if status == "completed":
        ensure_required_evidence_documents(problem_root)
    normalized_artifacts = validate_artifacts(artifacts, VALID_LEDGER_ARTIFACT_TYPES) if artifacts is not None else None
    ledger = load_ledger(problem_root)
    target_entry: dict | None = None
    for entry in ledger:
        if entry.get("run_id") == run_id:
            target_entry = entry
            break
    if target_entry is None:
        raise ValueError(f"Run not found in ledger: {run_id}")
    target_entry["status"] = status
    target_entry["finished"] = utc_now_iso()
    if verdict is not None:
        target_entry["verdict"] = verdict
    if normalized_artifacts is not None:
        target_entry["artifacts"] = enrich_artifacts(problem_root, normalized_artifacts, valid_types=VALID_LEDGER_ARTIFACT_TYPES)
    if notes is not None:
        target_entry["notes"] = notes
    path = write_ledger(problem_root, ledger)
    _sync_workflow_finish(
        repo_root,
        problem_id,
        route=str(target_entry.get("route") or "survey-first"),
        run_id=run_id,
        status=status,
        verdict=str(target_entry.get("verdict")) if target_entry.get("verdict") is not None else None,
    )
    generate_experiment_index(repo_root)
    generate_evidence_bundle(repo_root, problem_id)
    return path


def create_proof_result(
    *,
    repo_root: Path,
    problem_id: str,
    run_id: str,
    claim_label: str,
    claim_class: str,
    status: str,
    verifier_kind: str,
    toolchain: str,
    command: str,
    source_entry: str,
    proof_obligations_path: str = "input_files/proof_obligations.md",
    statement_spec_path: str = "input_files/statement_spec.md",
    artifacts: list[dict] | None = None,
    dependencies: list[str] | None = None,
    notes: str | None = None,
) -> Path:
    if claim_class not in VALID_CLAIM_CLASSES:
        raise ValueError(f"Claim class must be one of {sorted(VALID_CLAIM_CLASSES)}; got {claim_class}")
    if status not in VALID_PROOF_STATUSES:
        raise ValueError(f"Proof status must be one of {sorted(VALID_PROOF_STATUSES)}; got {status}")
    if verifier_kind not in VALID_VERIFIER_KINDS:
        raise ValueError(f"Verifier kind must be one of {sorted(VALID_VERIFIER_KINDS)}; got {verifier_kind}")
    problem_root = get_problem_root(repo_root, problem_id)
    source_entry = ensure_workspace_file_exists(problem_root, source_entry, label="Source entry")
    proof_obligations_path = ensure_workspace_file_exists(problem_root, proof_obligations_path, label="Proof obligations")
    statement_spec_path = ensure_workspace_file_exists(problem_root, statement_spec_path, label="Statement specification")
    normalized_artifacts = validate_artifacts(artifacts, VALID_PROOF_ARTIFACT_TYPES)
    enriched_artifacts = enrich_artifacts(problem_root, normalized_artifacts, valid_types=VALID_PROOF_ARTIFACT_TYPES)
    ledger = load_ledger(problem_root)
    target_entry: dict | None = None
    for entry in ledger:
        if entry.get("run_id") == run_id:
            target_entry = entry
            break
    if target_entry is None:
        raise ValueError(f"Run not found in ledger: {run_id}")

    result_root = problem_root / "artifacts" / "prover-results"
    result_root.mkdir(parents=True, exist_ok=True)
    result_path = result_root / f"{run_id}.yaml"
    result_payload = {
        "run_id": run_id,
        "problem_id": problem_id,
        "claim_label": claim_label,
        "claim_class": claim_class,
        "ledger_run_id": run_id,
        "proof_obligations_path": proof_obligations_path,
        "statement_spec_path": statement_spec_path,
        "source_entry": source_entry,
        "status": status,
        "proof_result_status": status,
        "promotion_gate": {
            "allowed_progression": ["draft", "verifier-checked", "formally-checked"],
            "current_step": status if status in {"draft", "verifier-checked", "formally-checked"} else "post-gate",
        },
        "verifier": {
            "kind": verifier_kind,
            "toolchain": toolchain,
            "command": command,
        },
        "updated_at": utc_now_iso(),
        "novelty_gate": "unchecked",
        "dependencies": dependencies or [],
        "artifacts": enriched_artifacts,
        "notes": notes or "",
    }
    result_path.write_text(yaml.safe_dump(result_payload, sort_keys=False, allow_unicode=True), encoding="utf-8")

    proof_result_artifact = {
        "path": f"artifacts/prover-results/{run_id}.yaml",
        "type": "prover-result",
        "checksum": compute_artifact_checksum(result_path),
        "size_bytes": result_path.stat().st_size,
    }
    existing_artifacts = target_entry.setdefault("artifacts", [])
    replaced = False
    for index, item in enumerate(existing_artifacts):
        if item.get("path") == proof_result_artifact["path"] and item.get("type") == proof_result_artifact["type"]:
            existing_artifacts[index] = proof_result_artifact
            replaced = True
            break
    if not replaced:
        existing_artifacts.append(proof_result_artifact)
    write_ledger(problem_root, ledger)
    _record_workflow_proof_result(
        repo_root,
        problem_id,
        run_id=run_id,
        proof_status=status,
        result_path=proof_result_artifact["path"],
        run_status=str(target_entry.get("status")) if target_entry.get("status") is not None else None,
    )
    generate_experiment_index(repo_root)
    generate_evidence_bundle(repo_root, problem_id)
    return result_path


def record_failure_pattern(
    *,
    repo_root: Path,
    problem_id: str,
    run_id: str,
    stage: str,
    category: str,
    summary: str,
    details: dict[str, Any] | None = None,
) -> Path:
    problem_root = get_problem_root(repo_root, problem_id)
    payload: dict[str, Any] = {
        "at": utc_now_iso(),
        "problem_id": problem_id,
        "run_id": run_id,
        "stage": stage,
        "category": category,
        "summary": summary,
        "details": details or {},
    }
    relative_path = append_workspace_jsonl(problem_root, FAILURE_CHANNEL_PATH, payload)

    ledger = load_ledger(problem_root)
    for entry in ledger:
        if entry.get("run_id") == run_id:
            artifacts = entry.setdefault("artifacts", [])
            already_linked = any(
                artifact.get("path") == relative_path and artifact.get("type") == "failure-pattern"
                for artifact in artifacts
            )
            if not already_linked:
                described = describe_workspace_file(problem_root, relative_path)
                artifacts.append(
                    {
                        "path": described["path"],
                        "type": "failure-pattern",
                        "checksum": described["checksum"],
                        "size_bytes": described["size_bytes"],
                    }
                )
            break
    write_ledger(problem_root, ledger)
    generate_experiment_index(repo_root)
    generate_evidence_bundle(repo_root, problem_id)
    return problem_root / relative_path


def parse_artifact_args(values: list[str] | None) -> list[dict]:
    artifacts: list[dict] = []
    for value in values or []:
        if ":" not in value:
            raise ValueError(f"Artifact arguments must be path:type; got {value}")
        path_value, artifact_type = value.rsplit(":", 1)
        artifacts.append({"path": path_value, "type": artifact_type})
    return artifacts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OMEGA local runner substrate")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="Open a new running experiment ledger entry")
    start_parser.add_argument("problem_id")
    start_parser.add_argument("--route", required=True, choices=sorted(VALID_ROUTES))
    start_parser.add_argument("--agent", required=True)
    start_parser.add_argument("--description", required=True)
    start_parser.add_argument("--parent-run")
    start_parser.add_argument("--bound")
    start_parser.add_argument("--model")
    start_parser.add_argument("--hardware")
    start_parser.add_argument("--bootstrap-lean", action="store_true")

    finish_parser = subparsers.add_parser("finish", help="Close a run in the experiment ledger")
    finish_parser.add_argument("problem_id")
    finish_parser.add_argument("run_id")
    finish_parser.add_argument("--status", required=True, choices=sorted(VALID_RUN_STATUSES - {"running"}))
    finish_parser.add_argument("--verdict", choices=sorted(VALID_VERDICTS))
    finish_parser.add_argument("--artifact", action="append")
    finish_parser.add_argument("--notes")

    proof_parser = subparsers.add_parser("proof-result", help="Create or update a prover-result artifact")
    proof_parser.add_argument("problem_id")
    proof_parser.add_argument("run_id")
    proof_parser.add_argument("--claim-label", required=True)
    proof_parser.add_argument("--claim-class", required=True, choices=sorted(VALID_CLAIM_CLASSES))
    proof_parser.add_argument("--status", required=True, choices=sorted(VALID_PROOF_STATUSES))
    proof_parser.add_argument("--verifier", required=True, choices=sorted(VALID_VERIFIER_KINDS))
    proof_parser.add_argument("--toolchain", required=True)
    proof_parser.add_argument("--verifier-command", required=True)
    proof_parser.add_argument("--source-entry", required=True)
    proof_parser.add_argument("--proof-obligations-path", default="input_files/proof_obligations.md")
    proof_parser.add_argument("--statement-spec-path", default="input_files/statement_spec.md")
    proof_parser.add_argument("--artifact", action="append")
    proof_parser.add_argument("--dependency", action="append")
    proof_parser.add_argument("--notes")

    failure_parser = subparsers.add_parser("failure-pattern", help="Append a run-level failure pattern event")
    failure_parser.add_argument("problem_id")
    failure_parser.add_argument("run_id")
    failure_parser.add_argument("--stage", required=True)
    failure_parser.add_argument("--category", required=True)
    failure_parser.add_argument("--summary", required=True)
    failure_parser.add_argument("--details", help="YAML/JSON scalar note for additional detail")

    subparsers.add_parser("generate-index", help="Regenerate the global experiment index")

    evidence_parser = subparsers.add_parser("evidence-bundle", help="Regenerate the per-problem evidence bundle")
    evidence_parser.add_argument("problem_id")

    bootstrap_parser = subparsers.add_parser("bootstrap-lean", help="Copy the Lean starter into a problem workspace")
    bootstrap_parser.add_argument("problem_id")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "start":
            run_id = start_run(
                repo_root=REPO_ROOT,
                problem_id=args.problem_id,
                route=args.route,
                agent=args.agent,
                description=args.description,
                parent_run=args.parent_run,
                bound=args.bound,
                model=args.model,
                hardware=args.hardware,
                bootstrap_lean=args.bootstrap_lean,
            )
            print(run_id)
            return 0
        if args.command == "finish":
            finish_run(
                repo_root=REPO_ROOT,
                problem_id=args.problem_id,
                run_id=args.run_id,
                status=args.status,
                verdict=args.verdict,
                artifacts=parse_artifact_args(args.artifact),
                notes=args.notes,
            )
            print(args.run_id)
            return 0
        if args.command == "proof-result":
            result_path = create_proof_result(
                repo_root=REPO_ROOT,
                problem_id=args.problem_id,
                run_id=args.run_id,
                claim_label=args.claim_label,
                claim_class=args.claim_class,
                status=args.status,
                verifier_kind=args.verifier,
                toolchain=args.toolchain,
                command=args.verifier_command,
                source_entry=args.source_entry,
                proof_obligations_path=args.proof_obligations_path,
                statement_spec_path=args.statement_spec_path,
                artifacts=parse_artifact_args(args.artifact),
                dependencies=args.dependency,
                notes=args.notes,
            )
            print(result_path)
            return 0
        if args.command == "failure-pattern":
            details: dict[str, Any] | None = None
            if args.details:
                details = {"note": args.details}
            path = record_failure_pattern(
                repo_root=REPO_ROOT,
                problem_id=args.problem_id,
                run_id=args.run_id,
                stage=args.stage,
                category=args.category,
                summary=args.summary,
                details=details,
            )
            print(path)
            return 0
        if args.command == "generate-index":
            generate_experiment_index(REPO_ROOT)
            print(REPO_ROOT / "research" / "active" / "experiment-index.yaml")
            return 0
        if args.command == "evidence-bundle":
            bundle_path = generate_evidence_bundle(REPO_ROOT, args.problem_id)
            print(bundle_path)
            return 0
        if args.command == "bootstrap-lean":
            target = bootstrap_lean_starter(REPO_ROOT, args.problem_id)
            print(target)
            return 0
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
