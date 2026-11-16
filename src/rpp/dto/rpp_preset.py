from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import config, dataclass_json, Undefined

from rpp.dto.rpp_extension import RPPExtension
from rpp.dto.rpp_object import RPPObject, type_field
from rpp.dto.rpp_preset_reference import RPPPresetReference
from rpp.dto.rpp_profile_reference import RPPProfileReference


@dataclass_json(undefined=Undefined.RAISE)
@dataclass(kw_only=True)
class RPPPreset(RPPObject):
    """The read view of the Preset Data Object (json §Preset Data Object). `schema` is onDemand: the Preset Schema, which
    `includeElements=schema` embeds."""
    at_type: str = type_field("preset")
    id: str
    name: str
    description: str
    version: str
    rpp_version: str = field(metadata=config(field_name="rppVersion"))
    url: Optional[str] = None
    base_presets: Optional[list[RPPPresetReference]] = field(default=None, metadata=config(field_name="basePresets"))
    extensions: list[RPPExtension]
    profiles: list[RPPProfileReference]
    bound_profiles: list[RPPProfileReference] = field(metadata=config(field_name="boundProfiles"))
    default_preset: bool = field(metadata=config(field_name="defaultPreset"))
    schema: Optional[dict] = None
