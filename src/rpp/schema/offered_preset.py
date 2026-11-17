from dataclasses import dataclass

from rpp.schema.reference import Reference
from rpp.schema.rpp_extension import RppExtension
from rpp.schema.rpp_preset import RppPreset
from rpp.schema.rpp_profile import RppProfile


@dataclass(frozen=True, kw_only=True, eq=False)
class OfferedPreset:
    """A preset one server offers (data-objects §Presets, §Profile Binding), flattened: `extensions` and `profiles` are
    those of its definition including its base presets', `bound_profiles` those the server binds to it, and `applicable`
    all of them with their base profiles, each once (data-objects §Applicable Profiles)."""
    definition: RppPreset
    extensions: tuple[RppExtension, ...]
    profiles: tuple[RppProfile, ...]
    bound_profiles: tuple[RppProfile, ...]
    applicable: tuple[RppProfile, ...]
    default: bool
    required: dict[str, frozenset[str]]       # per applicable profile, its required extensions, flattened

    @property
    def id(self) -> str:
        return self.definition.id

    @property
    def version(self) -> str:
        return self.definition.version

    @property
    def key(self) -> str:
        return self.definition.key

    @property
    def extension_ids(self) -> tuple[str, ...]:
        return tuple(extension.id for extension in self.extensions)

    @property
    def reference(self) -> Reference:
        return self.definition.reference
