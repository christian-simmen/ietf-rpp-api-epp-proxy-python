from dataclasses import dataclass
from typing import Optional

from extensions.planet_atmosphere.core.model.atmosphere import Atmosphere


@dataclass(frozen=True, kw_only=True)
class AtmosphereChanges:
    """A partial update of the members this extension adds to a planet: the atmosphere to set as a whole, or `removed`."""
    atmosphere: Optional[Atmosphere] = None
    removed: bool = False
