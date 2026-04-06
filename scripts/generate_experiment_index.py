#!/usr/bin/env python3
"""Regenerate the OMEGA experiment index from active ledgers."""

from omega_runner import REPO_ROOT, generate_experiment_index


def main(argv: list[str] | None = None) -> int:
    del argv
    generate_experiment_index(REPO_ROOT)
    print(REPO_ROOT / "research" / "active" / "experiment-index.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())