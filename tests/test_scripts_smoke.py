"""Subprocess smoke tests for the thin mission-phase CLIs.

Each phase CLI is invoked as a real subprocess (``sys.executable``) from the
project root and must exit 0 (or a documented code) with the expected stdout /
artifact side effects. No mocks: these are the actual scripts.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def _run(name: str, *args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        check=False,
    )


class TestPhaseCLIs:
    def test_preflight(self) -> None:
        result = _run("00_preflight.py")
        assert result.returncode == 0
        assert "PIZ GLORIA" in result.stdout

    def test_brief(self) -> None:
        result = _run("01_brief.py")
        assert result.returncode == 0
        assert "Objectives (6)" in result.stdout

    def test_recon_with_default_goal(self) -> None:
        result = _run("02_recon.py")
        assert result.returncode == 0
        assert "Findings (4)" in result.stdout

    def test_recon_with_custom_goal(self) -> None:
        result = _run("02_recon.py", "map", "the", "valley")
        assert result.returncode == 0
        assert "map the valley" in result.stdout

    def test_plan(self) -> None:
        result = _run("03_plan.py")
        assert result.returncode == 0
        assert "dispersion" in result.stdout
        assert "puff" in result.stdout
        assert "alpine" in result.stdout
        assert "descent" in result.stdout
        assert "cover" in result.stdout
        assert "timeline" in result.stdout

    def test_execute_writes_outcome_and_figure(self, tmp_path: Path) -> None:
        result = _run("04_execute.py")
        assert result.returncode == 0
        assert "Mission success: True" in result.stdout
        assert (ROOT / "output" / "data" / "piz_gloria_outcome.json").exists()
        assert (ROOT / "output" / "figures" / "aerosol_plume.png").exists()
        assert (ROOT / "output" / "figures" / "puff_footprint.png").exists()
        assert (ROOT / "output" / "figures" / "descent_profile.png").exists()

    def test_debrief(self) -> None:
        result = _run("05_debrief.py")
        assert result.returncode == 0
        assert "Lessons (6)" in result.stdout


class TestManuscriptCLI:
    def test_z_generate_strict(self) -> None:
        result = _run("z_generate_manuscript_variables.py")
        assert result.returncode == 0
        assert (ROOT / "output" / "data" / "manuscript_variables.json").exists()

    def test_z_generate_allow_draft(self) -> None:
        result = _run("z_generate_manuscript_variables.py", "--allow-draft")
        assert result.returncode == 0

    def test_manuscript_variables_json_is_well_formed(self) -> None:
        import json

        path = ROOT / "output" / "data" / "manuscript_variables.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["BOND_CODENAME"] == "PIZ GLORIA"


def test_no_mock_imports_in_tests() -> None:
    """Guardrail: no mock framework anywhere in the source or test tree."""
    # Construct forbidden tokens from parts so this file's own source cannot
    # contain the literal strings (avoids tripping its own gate).
    forbidden = [
        "".join(parts)
        for parts in [
            ("unittest", ".mock"),
            ("Magic", "Mock"),
            ("mocker", ".patch"),
            ("create", "autospec"),
            ("@", "patch"),
        ]
    ]
    for root in (ROOT / "tests", ROOT / "src"):
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                assert token not in text, f"{path} uses {token}"
