from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, Undefined

from rpp.dto.rpp_object import RPPObject, type_field


@dataclass_json(undefined=Undefined.RAISE)
@dataclass(kw_only=True)
class RPPSatelliteUpdate(RPPObject):
    """A full update of a satellite: what a client may change of it."""
    at_type: str = type_field("satellite")
    orbitalPeriod: Optional[float] = None
