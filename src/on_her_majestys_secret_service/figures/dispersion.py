"""Figure generation for PIZ GLORIA (tight, deterministic, matplotlib-Agg).

Renders the aerosol-plume ground-level concentration footprint and the alpine
route's grade profile into ``output/figures/``. All figures derive from the
pure domain functions; no random data.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

from on_her_majestys_secret_service.dispersion_model import (  # noqa: E402
    PlumeScenario,
    downwind_axis,
)

__all__ = ["render_dispersion_figure", "render_route_figure"]

FONT_SIZE = 11


def _style() -> None:
    plt.rcParams.update(
        {
            "font.size": FONT_SIZE,
            "axes.grid": True,
            "grid.alpha": 0.3,
            "figure.dpi": 150,
            "savefig.bbox": "tight",
        }
    )


def render_dispersion_figure(
    scenario: PlumeScenario,
    output_path: str | Path,
    *,
    max_distance: float = 3000.0,
) -> Path:
    """Render the downwind centerline concentration profile to a PNG."""
    _style()
    axis = downwind_axis(5.0, max_distance, 300, scenario)
    distances = axis["distance"]
    concentrations = axis["concentration"]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(distances, concentrations, color="#b91c1c", linewidth=2)
    ax.set_xlabel("Downwind distance (m)")
    ax.set_ylabel("Ground-level concentration (kg m$^{-3}$)")
    ax.set_title("PIZ GLORIA aerosol plume — centerline footprint")
    ax.set_yscale("log")
    fig.tight_layout()
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    return path


def render_route_figure(
    route: dict[str, object],
    output_path: str | Path,
) -> Path:
    """Render the planned route's cumulative elevation / grade profile."""
    _style()
    waypoints = route.get("waypoints", [])
    if not isinstance(waypoints, list):
        waypoints = []
    fig, ax = plt.subplots(figsize=(7, 4))
    if waypoints:
        east = [float(w[0]) for w in waypoints]
        elev = [float(w[2]) for w in waypoints]
        ax.plot(east, elev, color="#1d4ed8", linewidth=2, marker="o", markersize=3)
    ax.set_xlabel("Easting (m)")
    ax.set_ylabel("Elevation (m)")
    ax.set_title("PIZ GLORIA alpine route — elevation profile")
    fig.tight_layout()
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    return path
