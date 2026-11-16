from dataclasses import dataclass, field
from typing import Mapping, Optional


@dataclass(kw_only=True)
class SatelliteChanges:
    """A partial update of a satellite: the members to set, and those to remove (`cleared`: `orbitalPeriod`).
    `extensions` is as for `PlanetChanges`."""
    orbitalPeriod: Optional[float] = None
    cleared: frozenset[str] = frozenset()
    extensions: Mapping[str, object] = field(default_factory=dict)
