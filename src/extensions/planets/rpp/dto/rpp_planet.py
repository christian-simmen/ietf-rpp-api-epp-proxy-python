from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, Undefined

from extensions.planets.rpp.dto.rpp_satellite_reference import RPPSatelliteReference
from rpp.dto.rpp_auth_info import RPPAuthInfo
from rpp.dto.rpp_object import RPPObject, type_field
from rpp.dto.rpp_prov_metadata import RPPProvMetadata


@dataclass_json(undefined=Undefined.RAISE)
@dataclass(kw_only=True)
class RPPPlanet(RPPObject):
    """The planet of the planets extension, as a create sends it and a read shows it."""
    at_type: str = type_field("planet")
    id: str
    type: str
    radius: Optional[float] = None
    mass: Optional[float] = None
    authInfo: Optional[RPPAuthInfo] = None
    provMetadata: Optional[RPPProvMetadata] = None
    satellite: Optional[list[RPPSatelliteReference]] = None
