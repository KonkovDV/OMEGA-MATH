# Contributing to OMEGA

Thanks for contributing to OMEGA.

## Local Setup

```bash
python -m pip install -e .[all]
```

## Required Checks

Before opening a PR, run:

```bash
python scripts/verify_version_sync.py
python scripts/validate_registry.py
python -m pytest -q
```

## Pull Request Rules

1. Keep changes focused and atomic.
2. Update docs and metadata when behavior or release state changes.
3. Add or update tests for functional changes.
4. Do not include secrets, credentials, or internal-only data.

## Commit Message Format

Use concise conventional-style messages, for example:

- `feat: add phase2 decomposition guard`
- `fix: stabilize thomson phase1 multistart`
- `docs: update v0.6.0 remediation status`
