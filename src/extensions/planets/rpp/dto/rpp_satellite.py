from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, Undefined

from extensions.planets.rpp.dto.rpp_planet_reference import RPPPlanetReference
from rpp.dto.rpp_object import RPPObject, type_field
from rpp.dto.rpp_prov_metadata import RPPProvMetadata


@dataclass_json(undefined=Undefined.RAISE)
@dataclass(kw_only=True)
class RPPSatellite(RPPObject):
    """The satellite of the planets extension, as a create sends it and a read shows it."""
    at_type: str = type_field("satellite")
    id: str
    planet: RPPPlanetReference
    orbitalPeriod: Optional[float] = None
    provMetadata: Optional[RPPProvMetadata] = None
