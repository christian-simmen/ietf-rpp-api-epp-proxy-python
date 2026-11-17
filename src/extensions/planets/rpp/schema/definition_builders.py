"""The preset and profile definitions of the demo extensions, in the form a definition file states them (`RegisteredExtension.presets`
and `.profiles`). Each has a specification under docs/demo/ named after its key (`<key>-preset.md`, `<key>-profile.md`)."""
import json
from pathlib import Path

DOCS = "https://github.com/pawel-kow/ietf-rpp-api-epp-proxy-python/blob/main/docs/demo/"

VERSION = "1.0"


def preset_id(key: str) -> str:
    return f"org.example.rpp.preset.{key}"


def profile_id(key: str) -> str:
    return f"org.example.rpp.profile.{key}"


def _references(identifiers) -> list[dict]:
    return [{"id": identifier, "version": VERSION} for identifier in identifiers]


def preset(key: str, name: str, description: str, base_presets=(), extensions=(), profiles=()) -> dict:
    """A preset of the demo: `base_presets` and `profiles` are identifiers, `extensions` identifiers of extensions (all 1.0)."""
    return {"id": preset_id(key), "name": name, "description": description, "version": VERSION, "rppVersion": "1.0",
            "url": f"{DOCS}{key}-preset.md", "basePresets": _references(base_presets),
            "extensions": _references(extensions), "profiles": _references(profiles)}


def profile(key: str, name: str, description: str, schema: Path, required=(), base_profiles=()) -> dict:
    """A profile of the demo with its Profile Schema (the file copied from `.spec/` next to the extension)."""
    return {"id": profile_id(key), "name": name, "description": description, "version": VERSION, "rppVersion": "1.0",
            "url": f"{DOCS}{key}-profile.md", "baseProfiles": _references(base_profiles),
            "requiredExtensions": _references(required), "schema": json.loads(schema.read_text(encoding="utf-8"))}
