"""The presets and profiles an app knows: the definition files of the proxy (`schemas/presets/`, `schemas/profiles/`) and
those the registered extensions bring. Built once per app from its registry, so nothing is process-global: two apps in one
process can know different presets (D18). Which of them a server offers is `OfferedPresets`."""
import json
from pathlib import Path

import yaml

from registration import ExtensionRegistry
from rpp.schema.reference import Reference
from rpp.schema.rpp_preset import RppPreset
from rpp.schema.rpp_profile import RppProfile

FOLDER = Path(__file__).parent / "schemas"


def _references(items) -> tuple[Reference, ...]:
    return tuple(Reference(item["id"], str(item["version"])) for item in items or ())


def _preset(key: str, data: dict) -> RppPreset:
    return RppPreset(
        key=key, id=data["id"], name=data["name"], description=data["description"], version=str(data["version"]),
        rpp_version=str(data["rppVersion"]), url=data.get("url"), base_presets=_references(data.get("basePresets")),
        extensions=_references(data.get("extensions")), profiles=_references(data.get("profiles")))


def _profile(key: str, data: dict, schema: dict | None) -> RppProfile:
    return RppProfile(
        key=key, id=data["id"], name=data["name"], description=data["description"], version=str(data["version"]),
        rpp_version=str(data["rppVersion"]), url=data["url"], base_profiles=_references(data.get("baseProfiles")),
        required_extensions=_references(data.get("requiredExtensions")), schema=schema)


def _read(path: Path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


class Definitions:
    """The definitions by key, and by identifier. An identifier denotes one definition only, whatever its kind
    (data-objects §Profiles): a preset, a profile and an extension never share one."""

    def __init__(self, presets: dict[str, RppPreset], profiles: dict[str, RppProfile]):
        self.presets = presets
        self.profiles = profiles

    @classmethod
    def load(cls, registry: ExtensionRegistry | None = None, extension_ids=()) -> "Definitions":
        presets = {path.stem: _preset(path.stem, _read(path)) for path in sorted((FOLDER / "presets").glob("*.yaml"))}
        profiles = {}
        for path in sorted((FOLDER / "profiles").glob("*.yaml")):
            schema_file = path.with_suffix(".schema.json")
            schema = json.loads(schema_file.read_text(encoding="utf-8")) if schema_file.exists() else None
            profiles[path.stem] = _profile(path.stem, _read(path), schema)
        for extension in registry or ():
            for key, data in extension.presets.items():
                if key in presets:
                    raise ValueError(f"The extension {extension.id} brings the preset {key}, which exists")
                presets[key] = _preset(key, data)
            for key, data in extension.profiles.items():
                if key in profiles:
                    raise ValueError(f"The extension {extension.id} brings the profile {key}, which exists")
                profiles[key] = _profile(key, data, data.get("schema"))
        definitions = cls(presets, profiles)
        definitions._check_identifiers(extension_ids)
        return definitions

    def _check_identifiers(self, extension_ids) -> None:
        seen: dict[str, str] = {identifier: "an extension" for identifier in extension_ids}
        for kind, items in (("a preset", self.presets.values()), ("a profile", self.profiles.values())):
            for item in items:
                if item.id in seen:
                    raise ValueError(f"The identifier {item.id} denotes {seen[item.id]} and {kind}")
                seen[item.id] = kind

    def preset_by_reference(self, reference: Reference) -> RppPreset:
        for preset in self.presets.values():
            if preset.id == reference.id:
                if preset.version != reference.version:
                    raise ValueError(
                        f"The preset {reference.id} is referenced in version {reference.version}, "
                        f"the definition is version {preset.version}")
                return preset
        raise ValueError(f"The preset {reference.id} is referenced and not defined")

    def profile_by_reference(self, reference: Reference) -> RppProfile:
        for profile in self.profiles.values():
            if profile.id == reference.id:
                if profile.version != reference.version:
                    raise ValueError(
                        f"The profile {reference.id} is referenced in version {reference.version}, "
                        f"the definition is version {profile.version}")
                return profile
        raise ValueError(f"The profile {reference.id} is referenced and not defined")
