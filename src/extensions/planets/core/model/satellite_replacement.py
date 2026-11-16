from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class SatelliteReplacement:
    """A full update of a satellite: its read-write data elements as they are to be."""
    id: str
    orbitalPeriod: Optional[float] = None
