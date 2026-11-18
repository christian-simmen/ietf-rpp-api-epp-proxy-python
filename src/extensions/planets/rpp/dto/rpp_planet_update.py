from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, Undefined

from rpp.dto.rpp_auth_info import RPPAuthInfo
from rpp.dto.rpp_object import RPPObject, type_field


@dataclass_json(undefined=Undefined.RAISE)
@dataclass(kw_only=True)
class RPPPlanetUpdate(RPPObject):
    """A full update of a planet: what a client may change of it."""
    at_type: str = type_field("planet")
    type: str
    radius: Optional[float] = None
    mass: Optional[float] = None
    authInfo: Optional[RPPAuthInfo] = None
