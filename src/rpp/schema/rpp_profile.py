from dataclasses import dataclass

from rpp.schema.reference import Reference


@dataclass(frozen=True, kw_only=True, eq=False)
class RppProfile:
    """A profile (data-objects §Profiles) as its definition states it: it only constrains. The definition is the same on
    every server, so it is what the Profile Data Object publishes. `key` is what a configuration names it by.

    `base_profiles` and `required_extensions` are the direct ones, the Data Object flattens them. `schema` is the Profile
    Schema (json §Profile Schema) when the profile has one: JSON Schema cannot express every constraint.
    """
    key: str
    id: str
    name: str
    description: str
    version: str
    rpp_version: str
    url: str
    base_profiles: tuple[Reference, ...] = ()
    required_extensions: tuple[Reference, ...] = ()
    schema: dict | None = None

    @property
    def reference(self) -> Reference:
        return Reference(self.id, self.version)
