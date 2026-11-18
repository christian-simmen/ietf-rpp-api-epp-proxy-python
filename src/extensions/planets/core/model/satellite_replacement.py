from dataclasses import dataclass, field
from typing import Mapping, Optional


@dataclass(kw_only=True)
class SatelliteReplacement:
    """A full update of a satellite: its read-write data elements as they are to be."""
    id: str
    orbitalPeriod: Optional[float] = None
    extensions: Mapping[str, object] = field(default_factory=dict)
    # The extensions whose members this update replaces (those of the preset the request is under): one of them not given is
    # removed, the members of the others stay. None: every extension the backend holds.
    scope: Optional[frozenset[str]] = None
