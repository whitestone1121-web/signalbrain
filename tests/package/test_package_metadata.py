from __future__ import annotations

import os
import subprocess
import sys
import tomllib
from pathlib import Path

import signalbrain

ROOT = Path(__file__).resolve().parents[2]


def test_package_version_matches_pyproject():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert signalbrain.__version__ == pyproject["project"]["version"]


def test_cli_help_states_core_integrity_invariant():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    result = subprocess.run(
        [sys.executable, "-m", "signalbrain.cli", "--help"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "only byte-identical, human-merged receipts" in result.stdout
    assert "increase earned trust" in result.stdout
