"""Manuscript variable hydration for PIZ GLORIA.

Every ``{{TOKEN}}`` in ``manuscript/[0-9]*.md`` resolves through
:func:`generate_variables`, which reads ``manuscript/config.yaml`` plus the
live mission results computed by :func:`on_her_majestys_secret_service.mission.run_scenario`.
Metrics are never hand-authored in prose: they flow through this module so the
manuscript cannot drift from the code.
"""

from __future__ import annotations

import platform
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from on_her_majestys_secret_service.mission import CODENAME, PACKAGE_VERSION, run_scenario

__all__ = ["generate_variables", "load_manuscript_config", "resolve_manuscript_tree"]

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PACKAGE_ROOT / "manuscript" / "config.yaml"

_TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")


def load_manuscript_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load and validate ``manuscript/config.yaml`` (or an explicit path)."""
    path = Path(config_path) if config_path is not None else DEFAULT_CONFIG_PATH
    if not path.is_file():
        raise FileNotFoundError(f"manuscript config not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"manuscript config must be a top-level mapping, got {type(data).__name__}")
    return data


def generate_variables(
    *,
    config_path: str | Path | None = None,
    require_outputs: bool = True,
) -> dict[str, str]:
    """Compute the ``{{TOKEN}}`` -> value mapping for the manuscript.

    Args:
        config_path: Override for ``manuscript/config.yaml``.
        require_outputs: When True (default), compute the mission results via
            :func:`run_scenario` — the strict-mode gate that keeps real
            numbers (not ``N/A`` placeholders) in the manuscript.
    """
    config = load_manuscript_config(config_path)
    paper = config.get("paper", {})
    if not isinstance(paper, dict):
        raise ValueError("manuscript config 'paper' section must be a mapping")

    if require_outputs:
        results = run_scenario()
        dispersion = results["dispersion"]
        alpine = results["alpine"]
        cover = results["cover"]
        isopleth = f"{dispersion['isopleth_reach_m']} m"
        peak_c = f"{dispersion['peak_concentration_kg_m3']:.3e} kg m$^{{-3}}$"
        peak_dist = f"{dispersion['peak_distance_m']} m"
        route_dist = f"{alpine['route_distance_m']} m"
        route_grade = f"{alpine['route_mean_grade_deg']:.2f} deg"
        route_safe = "safe" if alpine["route_safe"] else "unsafe"
        bray_score = f"{cover['bray_score']:.3f}"
        bray_verdict = cover["bray_verdict"]
    else:
        isopleth = "N/A"
        peak_c = "N/A"
        peak_dist = "N/A"
        route_dist = "N/A"
        route_grade = "N/A"
        route_safe = "N/A"
        bray_score = "N/A"
        bray_verdict = "N/A"

    return {
        "BOND_FILM": "On Her Majesty's Secret Service",
        "BOND_CODENAME": CODENAME,
        "BOND_VERSION": PACKAGE_VERSION,
        "BOND_TITLE": str(paper.get("title", "")),
        "BOND_SUBTITLE": str(paper.get("subtitle", "")),
        "PIZ_ISOPLETH_REACH_M": str(isopleth),
        "PIZ_PEAK_CONCENTRATION": str(peak_c),
        "PIZ_PEAK_DISTANCE_M": str(peak_dist),
        "PIZ_ROUTE_DISTANCE_M": str(route_dist),
        "PIZ_ROUTE_MEAN_GRADE_DEG": str(route_grade),
        "PIZ_ROUTE_SAFE": str(route_safe),
        "PIZ_BRAY_SCORE": str(bray_score),
        "PIZ_BRAY_VERDICT": str(bray_verdict),
        "PYTHON_VERSION": platform.python_version(),
        "NUMPY_VERSION": np.__version__,
        "GENERATION_TIMESTAMP": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def resolve_manuscript_tree(
    variables: dict[str, str],
    *,
    manuscript_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    strict: bool = True,
) -> tuple[Path, list[str]]:
    """Copy each manuscript section to ``output/manuscript/``, substituting tokens.

    Only ``NN_*.md`` section files are copied (not sidecars such as
    ``SYNTAX.md``). In strict mode any leftover ``{{TOKEN}}`` fails the
    resolution so the manuscript can never render with raw braces.

    Returns the output directory and the sorted list of resolved file names.
    """
    manuscript_dir = Path(manuscript_dir) if manuscript_dir is not None else PACKAGE_ROOT / "manuscript"
    output_dir = Path(output_dir) if output_dir is not None else PACKAGE_ROOT / "output" / "manuscript"
    resolved: list[str] = []
    for source in sorted(manuscript_dir.glob("[0-9][0-9]_*.md")):
        text = source.read_text(encoding="utf-8")
        for token, value in variables.items():
            text = text.replace("{{" + token + "}}", value)
        unresolved = sorted(set(_TOKEN_RE.findall(text)))
        if unresolved and strict:
            raise ValueError(f"unresolved manuscript tokens in {source.name}: {unresolved}")
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / source.name).write_text(text, encoding="utf-8")
        resolved.append(source.name)
    return output_dir, resolved
