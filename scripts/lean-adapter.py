#!/usr/bin/env python3
"""Backwards-compatible wrapper — delegates to lean_adapter.main()."""
from lean_adapter import main  # type: ignore[import-untyped]

if __name__ == "__main__":
    main()
