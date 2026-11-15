from dataclasses import dataclass

from core.model.shared.profile_schema_reference import ProfileSchemaReference


@dataclass(kw_only=True)
class Discovery:
    version: str
    base_url: str
    tlds: list[str]
    environment_name: str
    environment_status: str
    objects: list[str]
    profiles: list[str]
    extensions: list[str]                  # the ids of the RPP extensions offered
    datetime: str
    profile_schemas: list[ProfileSchemaReference] | None = None   # None: the server publishes none
