from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, kw_only=True)
class Orbit:
    """The orbit of a satellite (docs/demo/satellite-orbit-extension.md): the semi-major axis in kilometres, the eccentricity
    and the inclination in degrees. It is the typed object that `Satellite.extensions` holds for this extension."""
    semiMajorAxis: float
    eccentricity: Optional[float] = None
    inclination: Optional[float] = None
