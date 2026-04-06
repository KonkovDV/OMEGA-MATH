#!/usr/bin/env python3
"""Backwards-compatible wrapper — delegates to cas_adapter.main()."""
from cas_adapter import main  # type: ignore[import-untyped]

if __name__ == "__main__":
    main()
