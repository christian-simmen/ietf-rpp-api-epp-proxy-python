from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, Undefined

from rpp.dto.rpp_discovery_environment import RPPDiscoveryEnvironment
from rpp.dto.rpp_discovery_version import RPPDiscoveryVersion
from rpp.dto.rpp_extension import RPPExtension
from rpp.dto.rpp_object import RPPObject, type_field
from rpp.dto.rpp_preset import RPPPreset
from rpp.dto.rpp_profile_reference import RPPProfileReference


@dataclass_json(undefined=Undefined.RAISE)
@dataclass(kw_only=True)
class RPPDiscovery(RPPObject):
    at_type: str = type_field("discovery")
    versions: list[RPPDiscoveryVersion]
    environment: RPPDiscoveryEnvironment
    tlds: list[str]
    extensions: Optional[list[RPPExtension]] = None
    presets: list[RPPPreset]
    profiles: Optional[list[RPPProfileReference]] = None
    objects: list[str]
    datetime: str
