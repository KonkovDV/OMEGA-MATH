#!/usr/bin/env python3
"""Tests for the OMEGA Python packaging and importable CLI surface."""

from __future__ import annotations

import importlib
import sys
import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"


class OmegaPythonSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        sys.path.insert(0, str(SCRIPTS_DIR))

    def test_pyproject_declares_python_first_cli_surface(self) -> None:
        pyproject_path = REPO_ROOT / "pyproject.toml"
        self.assertTrue(pyproject_path.exists(), "OMEGA should expose a pyproject packaging surface")

        pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        project = pyproject["project"]
        self.assertEqual(project["requires-python"], ">=3.12")
        self.assertIn("Private :: Do Not Upload", project["classifiers"])

        scripts = project["scripts"]
        self.assertEqual(scripts["omega-runner"], "omega_runner:main")
        self.assertEqual(scripts["omega-generate-index"], "generate_index:main")
        self.assertEqual(scripts["omega-generate-experiment-index"], "generate_experiment_index:main")
        self.assertEqual(scripts["omega-import-einstein-arena"], "import_einstein_arena:main")
        self.assertEqual(scripts["omega-scaffold-problem"], "scaffold_problem:main")
        self.assertEqual(scripts["omega-validate-registry"], "validate_registry:main")
        self.assertEqual(scripts["omega-query"], "experiment_query:main")
        self.assertEqual(scripts["omega-literature"], "literature_adapter:main")
        self.assertEqual(scripts["omega-lean"], "lean_adapter:main")
        self.assertEqual(scripts["omega-solve"], "solver_adapter:main")
        self.assertEqual(scripts["omega-cas"], "cas_adapter:main")
        self.assertEqual(scripts["omega-workflow"], "omega_workflow:main")
        self.assertEqual(scripts["omega-leancop-bridge"], "leancop_bridge:main")
        self.assertEqual(scripts["omega-proof-repair"], "proof_repair_loop:main")
        self.assertEqual(scripts["omega-verify-version-sync"], "verify_version_sync:main")

    def test_importable_cli_modules_exist(self) -> None:
        for module_name in (
            "omega_runner",
            "generate_index",
            "generate_experiment_index",
            "import_einstein_arena",
            "scaffold_problem",
            "validate_registry",
            "experiment_query",
            "literature_adapter",
            "lean_adapter",
            "solver_adapter",
            "cas_adapter",
            "omega_workflow",
            "leancop_bridge",
            "proof_repair_loop",
            "verify_version_sync",
        ):
            module = importlib.import_module(module_name)
            self.assertTrue(callable(getattr(module, "main", None)), f"{module_name} should expose main()")


if __name__ == "__main__":
    unittest.main()