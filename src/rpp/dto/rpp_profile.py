from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import config, dataclass_json, Undefined

from rpp.dto.rpp_extension import RPPExtension
from rpp.dto.rpp_object import RPPObject, type_field
from rpp.dto.rpp_profile_reference import RPPProfileReference


@dataclass_json(undefined=Undefined.RAISE)
@dataclass(kw_only=True)
class RPPProfile(RPPObject):
    """The Profile Data Object (json §6.11)."""
    at_type: str = type_field("profile")
    name: str
    description: str
    version: str
    rpp_version: str = field(metadata=config(field_name="rppVersion"))
    objects: list[str]
    extensions: Optional[list[RPPExtension]] = None
    base_profile: Optional[RPPProfileReference] = field(default=None, metadata=config(field_name="baseProfile"))
    default_profile: bool = field(metadata=config(field_name="defaultProfile"))
