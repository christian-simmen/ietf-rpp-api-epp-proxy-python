from dataclasses import dataclass, field
from typing import Mapping, Optional

from core.model.shared.common import AuthInfo


@dataclass(kw_only=True)
class PlanetChanges:
    """A partial update of a planet: the members to set, and those to remove (`cleared`: `radius`, `mass`). A member
    neither set nor cleared stays as it is. `extensions` holds the changes of the extensions that add members to the
    planet, by extension id, each a typed object that extension's own core defines; the backend applies each in the same
    transaction. Nothing of it is a JSON representation."""
    type: Optional[str] = None
    radius: Optional[float] = None
    mass: Optional[float] = None
    authInfo: Optional[AuthInfo] = None
    cleared: frozenset[str] = frozenset()
    extensions: Mapping[str, object] = field(default_factory=dict)
