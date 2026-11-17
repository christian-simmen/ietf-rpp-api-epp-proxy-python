from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, Undefined

from rpp.dto.rpp_object import RPPObject, type_field


@dataclass_json(undefined=Undefined.RAISE)
@dataclass(kw_only=True)
class RPPAtmosphere(RPPObject):
    """The member `atmosphere` of a planet, as a request sends it and a read shows it."""
    at_type: str = type_field("atmosphere")
    pressure: float
    dominantGas: Optional[str] = None
