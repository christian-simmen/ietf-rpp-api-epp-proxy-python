from dataclasses import dataclass

from dataclasses_json import dataclass_json, Undefined

from rpp.dto.rpp_object import RPPObject, type_field


@dataclass_json(undefined=Undefined.RAISE)
@dataclass(kw_only=True)
class RPPProfileReference(RPPObject):
    """The reference view of the Profile Data Object (json §Profile Data Object): the identifier and the version."""
    at_type: str = type_field("profile")
    id: str
    version: str
