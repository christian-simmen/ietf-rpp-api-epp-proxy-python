from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, Undefined

from rpp.dto.rpp_object import RPPObject, type_field


@dataclass_json(undefined=Undefined.RAISE)
@dataclass(kw_only=True)
class RPPOrbit(RPPObject):
    """The member `orbit` of a satellite, as a request sends it and a read shows it."""
    at_type: str = type_field("orbit")
    semiMajorAxis: float
    eccentricity: Optional[float] = None
    inclination: Optional[float] = None
