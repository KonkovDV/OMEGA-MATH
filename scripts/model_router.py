#!/usr/bin/env python3
"""OMEGA Model Router — unified LLM backend routing with profiles and fallbacks.

Provides a declarative routing layer that maps agent roles and task tiers
to specific model backends, manages API keys from environment, supports
health checks, and enables fallback chains.

This module is used by agent_orchestrator.py and can be invoked standalone
for health checks and profile inspection.

Design grounded in:
- DeepSeek-Prover-V2 two-level architecture (72B decomposes → 7B solves)
- OMEGA team.yaml tier routing rules
- LeanCopilot ExternalGenerator API pattern

Supported backends:
- openai:   OpenAI API (GPT-4o, o3-mini, etc.)
- deepseek: DeepSeek API (deepseek-chat, deepseek-reasoner)
- anthropic: Anthropic Claude API (claude-sonnet-4-20250514, claude-opus-4-20250514)
- ollama:   Local Ollama server (llama3, deepseek-prover-v2:7b, etc.)
- vllm:     Local vLLM server (any HuggingFace model)
- lmstudio: Local LM Studio server

Usage:
  python scripts/model_router.py profiles
  python scripts/model_router.py health
  python scripts/model_router.py resolve --role prover --tier T4-structural
  python scripts/model_router.py backends
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

import yaml

# ──────────────────────────── Backend Registry ────────────────────────────────


@dataclass
class Backend:
    """An LLM API backend."""

    name: str
    base_url: str
    api_key_env: str
    models: list[str] = field(default_factory=list)
    healthy: bool | None = None
    latency_ms: float | None = None

    @property
    def api_key(self) -> str:
        return os.environ.get(self.api_key_env, "")

    @property
    def is_configured(self) -> bool:
        """Check if the backend has a valid API key or is a local server."""
        if self.name in ("ollama", "vllm", "lmstudio"):
            return True  # Local servers don't need keys
        return bool(self.api_key)


BACKENDS: dict[str, Backend] = {
    "openai": Backend(
        name="openai",
        base_url="https://api.openai.com/v1",
        api_key_env="OPENAI_API_KEY",
        models=["gpt-4o", "gpt-4o-mini", "o3-mini"],
    ),
    "deepseek": Backend(
        name="deepseek",
        base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        api_key_env="DEEPSEEK_API_KEY",
        models=["deepseek-chat", "deepseek-reasoner"],
    ),
    "anthropic": Backend(
        name="anthropic",
        base_url="https://api.anthropic.com/v1",
        api_key_env="ANTHROPIC_API_KEY",
        models=["claude-sonnet-4-20250514", "claude-opus-4-20250514"],
    ),
    "ollama": Backend(
        name="ollama",
        base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        api_key_env="OLLAMA_API_KEY",
        models=["deepseek-prover-v2:7b", "llama3", "qwen2.5-coder"],
    ),
    "vllm": Backend(
        name="vllm",
        base_url=os.environ.get("VLLM_BASE_URL", "http://localhost:8000/v1"),
        api_key_env="VLLM_API_KEY",
        models=["deepseek-prover-v2-7b"],
    ),
    "lmstudio": Backend(
        name="lmstudio",
        base_url=os.environ.get("LMSTUDIO_BASE_URL", "http://localhost:1234/v1"),
        api_key_env="LMSTUDIO_API_KEY",
        models=[],
    ),
}


# ──────────────────────────── Model Profiles ──────────────────────────────────


@dataclass
class ModelProfile:
    """A model routing profile for a specific use case."""

    model: str
    backend: str
    max_tokens: int
    temperature: float
    description: str
    fallback: str | None = None


# Role → tier → model profile (the routing table)
# Designed for two-level architecture: big model plans, small model executes.
PROFILES: dict[str, dict[str, ModelProfile]] = {
    "planner": {
        "default": ModelProfile("deepseek-chat", "deepseek", 2000, 0.3, "Planning and triage", fallback="gpt-4o-mini"),
        "T4-structural": ModelProfile("deepseek-reasoner", "deepseek", 3000, 0.2, "Proof-strategy planning needs reasoning", fallback="claude-sonnet-4-20250514"),
        "T5-foundational": ModelProfile("deepseek-reasoner", "deepseek", 3000, 0.2, "Foundational planning needs reasoning", fallback="claude-sonnet-4-20250514"),
    },
    "librarian": {
        "default": ModelProfile("deepseek-chat", "deepseek", 3000, 0.2, "Literature synthesis", fallback="gpt-4o-mini"),
    },
    "analyst": {
        "default": ModelProfile("deepseek-chat", "deepseek", 4000, 0.3, "Hypothesis generation and analysis", fallback="gpt-4o"),
    },
    "experimentalist": {
        "default": ModelProfile("deepseek-chat", "deepseek", 4000, 0.4, "Experiment design", fallback="gpt-4o"),
        "local": ModelProfile("deepseek-prover-v2:7b", "ollama", 4000, 0.3, "Local experiment with prover model"),
    },
    "prover": {
        "default": ModelProfile("deepseek-reasoner", "deepseek", 6000, 0.1, "Proof search and formal reasoning", fallback="claude-opus-4-20250514"),
        "local": ModelProfile("deepseek-prover-v2:7b", "ollama", 8000, 0.1, "Local 7B prover for subgoal solving"),
    },
    "writer": {
        "default": ModelProfile("deepseek-chat", "deepseek", 8000, 0.4, "Drafting research notes", fallback="claude-sonnet-4-20250514"),
    },
    "reviewer": {
        "default": ModelProfile("deepseek-chat", "deepseek", 3000, 0.2, "Critical review and referee reports", fallback="gpt-4o"),
    },
}


# ──────────────────────────── Routing Logic ───────────────────────────────────


def resolve_profile(
    role: str,
    tier: str = "default",
    *,
    prefer_local: bool = False,
) -> ModelProfile:
    """Resolve the best model profile for a given role and tier.

    Args:
        role: Agent role (planner, librarian, analyst, experimentalist, prover, writer, reviewer).
        tier: Problem tier from triage (T1-computational, T2-experimental, etc.) or "default".
        prefer_local: If True, prefer local backends (ollama, vllm, lmstudio) when available.

    Returns:
        The resolved ModelProfile.
    """
    role_profiles = PROFILES.get(role)
    if not role_profiles:
        return ModelProfile("deepseek-chat", "deepseek", 4000, 0.3, f"Fallback for unknown role: {role}")

    if prefer_local and "local" in role_profiles:
        return role_profiles["local"]

    # Try tier-specific profile first
    if tier != "default" and tier in role_profiles:
        return role_profiles[tier]

    return role_profiles["default"]


def resolve_backend(profile: ModelProfile) -> Backend:
    """Get the Backend object for a profile."""
    return BACKENDS.get(profile.backend, BACKENDS["deepseek"])


def resolve_with_fallback(
    role: str,
    tier: str = "default",
    *,
    prefer_local: bool = False,
) -> tuple[ModelProfile, Backend]:
    """Resolve profile and verify backend is configured, falling back if needed.

    Returns:
        Tuple of (profile, backend) where backend.is_configured is True,
        or the best available option if no fallback is configured.
    """
    profile = resolve_profile(role, tier, prefer_local=prefer_local)
    backend = resolve_backend(profile)

    if backend.is_configured:
        return profile, backend

    # Try fallback model
    if profile.fallback:
        fallback_backend_name = _infer_backend(profile.fallback)
        fallback_backend = BACKENDS.get(fallback_backend_name)
        if fallback_backend and fallback_backend.is_configured:
            fallback_profile = ModelProfile(
                model=profile.fallback,
                backend=fallback_backend_name,
                max_tokens=profile.max_tokens,
                temperature=profile.temperature,
                description=f"Fallback for {profile.model}",
            )
            return fallback_profile, fallback_backend

    # Return original even if unconfigured (caller decides what to do)
    return profile, backend


def _infer_backend(model: str) -> str:
    """Infer backend name from model string."""
    m = model.lower()
    if "claude" in m:
        return "anthropic"
    if "deepseek" in m:
        if ":" in m:
            return "ollama"  # deepseek-prover-v2:7b is Ollama format
        return "deepseek"
    if "gpt" in m or "o3" in m or "o1" in m:
        return "openai"
    if "llama" in m or "qwen" in m or "mistral" in m:
        return "ollama"
    return "openai"


# ──────────────────────────── Health Checks ───────────────────────────────────


def check_backend_health(backend: Backend, *, timeout: float = 5.0) -> Backend:
    """Check if a backend is reachable and measure latency."""
    if not backend.is_configured:
        backend.healthy = False
        return backend

    try:
        start = time.monotonic()

        if backend.name == "ollama":
            url = f"{backend.base_url}/api/tags"
            req = urllib.request.Request(url, method="GET")
        elif backend.name == "anthropic":
            # Anthropic doesn't have a simple health endpoint; skip network check
            backend.healthy = True
            backend.latency_ms = 0.0
            return backend
        else:
            url = f"{backend.base_url}/models"
            headers = {"Authorization": f"Bearer {backend.api_key}"}
            req = urllib.request.Request(url, headers=headers, method="GET")

        with urllib.request.urlopen(req, timeout=timeout):
            pass
        backend.latency_ms = round((time.monotonic() - start) * 1000, 1)
        backend.healthy = True
    except (urllib.error.URLError, OSError, TimeoutError):
        backend.healthy = False
        backend.latency_ms = None

    return backend


def check_all_backends(*, timeout: float = 5.0) -> list[dict[str, Any]]:
    """Check health of all configured backends."""
    results = []
    for name, backend in BACKENDS.items():
        check_backend_health(backend, timeout=timeout)
        results.append({
            "name": name,
            "configured": backend.is_configured,
            "healthy": backend.healthy,
            "latency_ms": backend.latency_ms,
            "base_url": backend.base_url,
            "models": backend.models,
        })
    return results


# ──────────────────────────── CLI ─────────────────────────────────────────────


def cmd_profiles() -> None:
    """Print all model profiles in a readable format."""
    output: dict[str, Any] = {}
    for role, tiers in PROFILES.items():
        output[role] = {}
        for tier, profile in tiers.items():
            output[role][tier] = {
                "model": profile.model,
                "backend": profile.backend,
                "max_tokens": profile.max_tokens,
                "temperature": profile.temperature,
                "description": profile.description,
                "fallback": profile.fallback,
            }
    print(yaml.safe_dump(output, sort_keys=False, allow_unicode=True))


def cmd_health() -> None:
    """Check and print backend health status."""
    results = check_all_backends()
    for r in results:
        status = "OK" if r["healthy"] else ("UNCONFIGURED" if not r["configured"] else "DOWN")
        latency = f" ({r['latency_ms']}ms)" if r["latency_ms"] is not None else ""
        print(f"  {r['name']:12s} {status:14s}{latency}  {r['base_url']}")
    print()

    configured = sum(1 for r in results if r["configured"])
    healthy = sum(1 for r in results if r["healthy"])
    print(f"Configured: {configured}/{len(results)}, Healthy: {healthy}/{len(results)}")


def cmd_resolve(role: str, tier: str, prefer_local: bool) -> None:
    """Resolve and print the model profile for a role/tier combo."""
    profile, backend = resolve_with_fallback(role, tier, prefer_local=prefer_local)
    result = {
        "role": role,
        "tier": tier,
        "prefer_local": prefer_local,
        "resolved": {
            "model": profile.model,
            "backend": profile.backend,
            "max_tokens": profile.max_tokens,
            "temperature": profile.temperature,
            "description": profile.description,
        },
        "backend_configured": backend.is_configured,
    }
    if profile.fallback:
        result["fallback_available"] = profile.fallback
    print(yaml.safe_dump(result, sort_keys=False, allow_unicode=True))


def cmd_backends() -> None:
    """List all registered backends."""
    output: list[dict[str, Any]] = []
    for name, backend in BACKENDS.items():
        output.append({
            "name": name,
            "base_url": backend.base_url,
            "api_key_env": backend.api_key_env,
            "configured": backend.is_configured,
            "models": backend.models,
        })
    print(yaml.safe_dump(output, sort_keys=False, allow_unicode=True))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="omega-model-router",
        description="OMEGA Model Router — LLM backend routing, profiles, and health checks.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("profiles", help="Show all model profiles")
    sub.add_parser("health", help="Check backend health")
    sub.add_parser("backends", help="List registered backends")

    resolve_p = sub.add_parser("resolve", help="Resolve a profile for a role/tier")
    resolve_p.add_argument("--role", required=True, help="Agent role")
    resolve_p.add_argument("--tier", default="default", help="Problem tier")
    resolve_p.add_argument("--prefer-local", action="store_true", help="Prefer local backends")

    args = parser.parse_args()

    if args.command == "profiles":
        cmd_profiles()
    elif args.command == "health":
        cmd_health()
    elif args.command == "resolve":
        cmd_resolve(args.role, args.tier, args.prefer_local)
    elif args.command == "backends":
        cmd_backends()


if __name__ == "__main__":
    main()
