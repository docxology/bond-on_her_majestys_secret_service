"""on_her_majestys_secret_service — BOND film package, mission codename PIZ GLORIA.

Domain modules (infrastructure-free, importable without bond-api):

* :mod:`~.dispersion_model` — aerosol bioweapon dispersion (Gaussian plume +
  valley transport).
* :mod:`~.puff_dispersion` — Lagrangian Gaussian puff train (time-dependent
  dispersion / early-warning arrival).
* :mod:`~.alpine_routes` — bobsleigh-grade alpine route planning & slope safety.
* :mod:`~.descent_dynamics` — bobsleigh descent kinematics + banked-curve physics.
* :mod:`~.cover_identity` — cover-identity risk scoring (the Bray persona).
* :mod:`~.identity_timeline` — cover-timeline verification (interval consistency).

:mod:`~.mission` is the thin adapter implementing the frozen
``bond_api.MissionProvider`` protocol for the orchestrator.
"""

from __future__ import annotations

from on_her_majestys_secret_service import (
    alpine_routes,
    cover_identity,
    descent_dynamics,
    dispersion_model,
    identity_timeline,
    mission,
    puff_dispersion,
)
from on_her_majestys_secret_service.mission import MissionProvider

__version__ = "0.1.0"

__all__ = [
    "MissionProvider",
    "alpine_routes",
    "cover_identity",
    "descent_dynamics",
    "dispersion_model",
    "identity_timeline",
    "mission",
    "puff_dispersion",
]
