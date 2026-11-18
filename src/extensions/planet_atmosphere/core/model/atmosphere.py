from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, kw_only=True)
class Atmosphere:
    """The atmosphere of a planet (docs/demo/planet-atmosphere-extension.md): the pressure at the surface in bar and the gas
    that makes up most of it. It is the typed object that `Planet.extensions` holds for this extension."""
    pressure: float
    dominantGas: Optional[str] = None
