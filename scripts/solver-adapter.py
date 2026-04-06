#!/usr/bin/env python3
"""Backwards-compatible wrapper — delegates to solver_adapter.main()."""
from solver_adapter import main  # type: ignore[import-untyped]

if __name__ == "__main__":
    main()
