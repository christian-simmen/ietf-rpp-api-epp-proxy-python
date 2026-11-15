from dataclasses import dataclass

from dataclasses_json import dataclass_json, Undefined

from rpp.dto.rpp_object import RPPObject, type_field


@dataclass_json(undefined=Undefined.RAISE)
@dataclass(kw_only=True)
class RPPProfileReference(RPPObject):
    """The Profile Reference Object (json §6.11)."""
    at_type: str = type_field("profile")
    name: str
