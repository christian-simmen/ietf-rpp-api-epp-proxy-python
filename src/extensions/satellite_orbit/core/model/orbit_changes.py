from dataclasses import dataclass
from typing import Optional

from extensions.satellite_orbit.core.model.orbit import Orbit


@dataclass(frozen=True, kw_only=True)
class OrbitChanges:
    """A partial update of the members this extension adds to a satellite: the orbit to set as a whole, or `removed`."""
    orbit: Optional[Orbit] = None
    removed: bool = False
