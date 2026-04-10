"""Needed to explain that this is a package."""

from __future__ import annotations

from .numpydt_scalar_interval import NPScalarInterval
from .scalar_interval import ScalarInterval

__all__: list[str] = ["ScalarInterval", "NPScalarInterval"]
