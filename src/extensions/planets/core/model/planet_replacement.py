from dataclasses import dataclass
from typing import Optional

from core.model.shared.common import AuthInfo


@dataclass(kw_only=True)
class PlanetReplacement:
    """A full update of a planet: its read-write data elements as they are to be. Without `authInfo` the planet keeps
    its own."""
    id: str
    type: str
    radius: Optional[float] = None
    mass: Optional[float] = None
    authInfo: Optional[AuthInfo] = None
