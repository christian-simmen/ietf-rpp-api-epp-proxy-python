"""Inheritance of presets and profiles (data-objects §Inheritance of Presets and Profiles): a union without overriding, each
item once. A cycle, and one extension in two versions, are refused with what conflicts."""
from rpp.schema.definitions import Definitions
from rpp.schema.reference import Reference
from rpp.schema.rpp_preset import RppPreset
from rpp.schema.rpp_profile import RppProfile


def _add_extensions(found: dict[str, Reference], items, owner: str) -> None:
    for item in items:
        known = found.get(item.id)
        if known is not None and known.version != item.version:
            raise ValueError(f"{owner} contains the extension {item.id} in the versions {known.version} and {item.version}")
        found.setdefault(item.id, item)


class PresetFlattening:
    def __init__(self, definitions: Definitions):
        self._definitions = definitions

    def presets(self, preset: RppPreset, path=()) -> list[RppPreset]:
        """The preset and its base presets, directly or indirectly, each once."""
        if preset.id in path:
            raise ValueError(f"The preset {preset.id} builds on itself: {' -> '.join((*path, preset.id))}")
        found = [preset]
        for reference in preset.base_presets:
            for base in self.presets(self._definitions.preset_by_reference(reference), (*path, preset.id)):
                if base not in found:
                    found.append(base)
        return found

    def extensions(self, preset: RppPreset) -> tuple[Reference, ...]:
        found: dict[str, Reference] = {}
        for item in self.presets(preset):
            _add_extensions(found, item.extensions, f"The preset {preset.id}")
        return tuple(found.values())

    def profiles(self, preset: RppPreset) -> tuple[RppProfile, ...]:
        found: list[RppProfile] = []
        for item in self.presets(preset):
            for reference in item.profiles:
                profile = self._definitions.profile_by_reference(reference)
                if profile not in found:
                    found.append(profile)
        return tuple(found)

    def profile_bases(self, profile: RppProfile, path=()) -> list[RppProfile]:
        """The base profiles, directly or indirectly, and the profile, each once, the bases first."""
        if profile.id in path:
            raise ValueError(f"The profile {profile.id} builds on itself: {' -> '.join((*path, profile.id))}")
        found: list[RppProfile] = []
        for reference in profile.base_profiles:
            for base in self.profile_bases(self._definitions.profile_by_reference(reference), (*path, profile.id)):
                if base not in found:
                    found.append(base)
        if profile not in found:
            found.append(profile)
        return found

    def required_extensions(self, profile: RppProfile) -> tuple[Reference, ...]:
        found: dict[str, Reference] = {}
        for item in self.profile_bases(profile):
            _add_extensions(found, item.required_extensions, f"The profile {profile.id}")
        return tuple(found.values())

    def applicable(self, profiles) -> tuple[RppProfile, ...]:
        found: list[RppProfile] = []
        for profile in profiles:
            for item in self.profile_bases(profile):
                if item not in found:
                    found.append(item)
        return tuple(found)
