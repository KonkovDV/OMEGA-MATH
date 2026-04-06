#!/usr/bin/env python3
"""Backwards-compatible wrapper — delegates to experiment_query.main()."""
from experiment_query import main  # type: ignore[import-untyped]

if __name__ == "__main__":
    main()
