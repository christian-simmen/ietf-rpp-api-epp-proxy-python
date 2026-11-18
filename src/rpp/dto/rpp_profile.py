from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import config, dataclass_json, Undefined

from rpp.dto.rpp_extension import RPPExtension
from rpp.dto.rpp_object import RPPObject, type_field
from rpp.dto.rpp_profile_reference import RPPProfileReference


@dataclass_json(undefined=Undefined.RAISE)
@dataclass(kw_only=True)
class RPPProfile(RPPObject):
    """The read view of the Profile Data Object (json §Profile Data Object)."""
    at_type: str = type_field("profile")
    id: str
    name: str
    description: str
    version: str
    rpp_version: str = field(metadata=config(field_name="rppVersion"))
    url: str
    base_profiles: Optional[list[RPPProfileReference]] = field(default=None, metadata=config(field_name="baseProfiles"))
    required_extensions: Optional[list[RPPExtension]] = field(default=None, metadata=config(field_name="requiredExtensions"))
