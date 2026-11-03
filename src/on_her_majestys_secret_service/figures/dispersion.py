"""Figure generation for PIZ GLORIA (tight, deterministic, matplotlib-Agg).

Renders the aerosol-plume ground-level concentration footprint and the alpine
route's grade profile into ``output/figures/``. All figures derive from the
pure domain functions; no random data.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from on_her_majestys_secret_service.dispersion_model import (
    PlumeScenario,
    downwind_axis,
)
from on_her_majestys_secret_service.puff_dispersion import puff_field_time_series

__all__ = [
    "render_descent_figure",
    "render_dispersion_figure",
    "render_puff_figure",
    "render_route_figure",
]

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


def render_puff_figure(
    scenario: PlumeScenario,
    output_path: str | Path,
    *,
    receptor_x: float = 2000.0,
) -> Path:
    """Render the puff concentration time series at a downwind receptor."""
    _style()
    series = puff_field_time_series(
        scenario,
        receptor_x,
        0.0,
        1.5,
        t_start=0.0,
        t_end=1500.0,
        dt=10.0,
    )
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(series["time"], series["concentration"], color="#b45309", linewidth=2)
    ax.set_xlabel("Time since release (s)")
    ax.set_ylabel("Concentration (kg m$^{-3}$)")
    ax.set_title("PIZ GLORIA puff footprint at downstream receptor")
    ax.set_yscale("log")
    fig.tight_layout()
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    return path


def render_descent_figure(
    descent: dict[str, object],
    output_path: str | Path,
) -> Path:
    """Render the bobsleigh descent speed vs distance profile."""
    _style()
    dists = descent.get("distance", [])
    speeds = descent.get("speed", [])
    fig, ax = plt.subplots(figsize=(7, 4))
    if isinstance(dists, list) and isinstance(speeds, list) and dists and speeds:
        ax.plot(
            [float(d) for d in dists],
            [float(v) for v in speeds],
            color="#15803d",
            linewidth=2,
        )
    ax.set_xlabel("Distance along track (m)")
    ax.set_ylabel("Speed (m s$^{-1}$)")
    ax.set_title("PIZ GLORIA bobsleigh descent — speed profile")
    fig.tight_layout()
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    return path
