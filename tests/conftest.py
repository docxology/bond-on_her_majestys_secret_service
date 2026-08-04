"""Shared pytest configuration for PIZ GLORIA.

Adds ``src/`` to ``sys.path`` so project modules import without installation,
and pins matplotlib to the non-interactive Agg backend so figure tests never
open display windows (deterministic, headless).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
