"""on_her_majestys_secret_service — BOND film package, mission codename PIZ GLORIA.

Domain modules (infrastructure-free, importable without bond-api):

* :mod:`~.dispersion_model` — aerosol bioweapon dispersion (Gaussian plume +
  valley transport).
* :mod:`~.alpine_routes` — bobsleigh-grade alpine route planning & slope safety.
* :mod:`~.cover_identity` — cover-identity risk scoring (the Bray persona).

:mod:`~.mission` is the thin adapter implementing the frozen
``bond_api.MissionProvider`` protocol for the orchestrator.
"""

from __future__ import annotations

from on_her_majestys_secret_service import (
    alpine_routes,
    cover_identity,
    dispersion_model,
    mission,
)
from on_her_majestys_secret_service.mission import MissionProvider

__version__ = "0.1.0"

__all__ = [
    "MissionProvider",
    "alpine_routes",
    "cover_identity",
    "dispersion_model",
    "mission",
]
