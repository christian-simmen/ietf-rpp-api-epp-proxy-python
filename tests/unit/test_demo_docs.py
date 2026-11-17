"""The specifications under docs/demo/ of the demo extensions, profiles and presets (#179), each in the format of the extension
guidelines, against the definitions the proxy registers.

- An extension specification (`<key>-extension.md`): every example marked `<!-- example valid|invalid <definition> -->` validates, or
  fails, against the Effective Schema of a server that supports the planets extension and the extension, every definition it shows
  (`<!-- definition <name> -->`) is the one of the schema, and the schema in the package is the one of `.spec/`.
- A profile specification (`<key>-profile.md`): the Profile Schema it shows is the file, `<!-- example valid <definition> -->` is
  valid with and without the profile, `<!-- example violates <definition> -->` is valid without it and refused with it (step 2),
  as the guidelines require of every constraint.
- A preset specification (`<key>-preset.md`): the Preset Overview is the definition the proxy registers."""
import json
import re
from pathlib import Path

import pytest
from jsonschema import ValidationError

from registration import load_extensions
from rpp.schema.definitions import Definitions
from rpp.schema.extension_registration import register_all
from rpp.schema.extensions import EXTENSIONS
from rpp.schema.offered_presets import OfferedPresets
from rpp.schema.profile_constraint_violation import ProfileConstraintViolation
from rpp.schema.schema_scope import SchemaScope
from rpp.schema.validator import validate_schema

pytestmark = pytest.mark.lazy_schemas

ROOT = Path(__file__).parents[2]
DEMO = ROOT / "docs" / "demo"
SPEC = ROOT / ".spec"

REGISTRY = load_extensions(["extensions.planets", "extensions.planet_atmosphere", "extensions.satellite_orbit"])
register_all(REGISTRY)
DEFINITIONS = Definitions.load(REGISTRY, EXTENSIONS)

PLANETS = "org.example.rpp.extension.planets"
EXAMPLE = re.compile(r"<!-- example (valid|invalid|violates) ([\w.]+) -->\n```json\n(.*?)```", re.DOTALL)
DEFINITION = re.compile(r"<!-- definition ([\w.]+) -->\n```json\n(.*?)```", re.DOTALL)
PACKAGES = {"planet-atmosphere": "planet_atmosphere", "satellite-orbit": "satellite_orbit"}


def read(name):
    return (DEMO / name).read_text(encoding="utf-8")


def examples(text):
    return [(kind, name, json.loads(body)) for kind, name, body in EXAMPLE.findall(text)]


def table(text):
    """The rows of the first table of a document by field."""
    return {cells[0]: cells[1] for cells in (
        [cell.strip() for cell in line.strip("|").split("|", 1)] for line in text.splitlines() if line.startswith("| "))
        if cells[0] not in ("Field", "-----")}


# --- extensions

@pytest.mark.parametrize("key", PACKAGES)
def test_an_extension_specification_has_valid_and_invalid_examples_that_validate_as_they_say(key):
    schema = json.loads((SPEC / f"{key}-extension.schema.json").read_text(encoding="utf-8"))
    extensions = (PLANETS, schema["rpp:extension"]["id"])
    found = examples(read(f"{key}-extension.md"))

    assert {kind for kind, _, _ in found} == {"valid", "invalid"}
    for kind, name, example in found:
        if kind == "valid":
            validate_schema(name, example, extensions=extensions)
        else:
            with pytest.raises((ValidationError, ValueError)):
                validate_schema(name, example, extensions=extensions)


@pytest.mark.parametrize("key", PACKAGES)
def test_an_extension_specification_shows_every_definition_of_its_schema_and_the_mapping(key):
    schema = json.loads((SPEC / f"{key}-extension.schema.json").read_text(encoding="utf-8"))
    text = read(f"{key}-extension.md")
    shown = {name: json.loads(body) for name, body in DEFINITION.findall(text)}

    assert sorted(shown) == sorted(schema["$defs"])
    assert all(shown[name] == {"$defs": {name: schema["$defs"][name]}} for name in shown)
    blocks = [json.loads(body) for body in re.findall(r"```json\n(.*?)```", text, re.DOTALL)]
    assert {"rpp:extends": schema["rpp:extends"]} in blocks and {"rpp:extension": schema["rpp:extension"]} in blocks
    overview = table(text)
    assert overview["Identifier"] == f"`{schema['rpp:extension']['id']}`" and overview["Schema `$id`"] == f"<{schema['$id']}>"


@pytest.mark.parametrize("key", PACKAGES)
def test_the_schema_in_the_package_is_the_one_of_the_specification(key):
    copy = ROOT / "src" / "extensions" / PACKAGES[key] / "rpp" / "schema" / f"{key}-extension.schema.json"

    assert json.loads(copy.read_text(encoding="utf-8")) == json.loads((SPEC / f"{key}-extension.schema.json").read_text(encoding="utf-8"))


# --- profiles

PROFILE_KEYS = ("rocky-planets", "catalogued-satellites", "habitable-atmospheres", "habitable-rocky-planets")


def scopes(key):
    """The scope of a preset with every demo extension without the profile, and the same with the profile bound to it."""
    without = OfferedPresets.build(DEFINITIONS, ["planets-complete"], "planets-complete", {}, tuple(EXTENSIONS)).offered[0]
    with_ = OfferedPresets.build(DEFINITIONS, ["planets-complete"], "planets-complete", {"planets-complete": [key]},
                                 tuple(EXTENSIONS)).offered[0]
    return (SchemaScope(without.extensions, without.applicable, without.required),
            SchemaScope(with_.extensions, with_.applicable, with_.required))


@pytest.mark.parametrize("key", PROFILE_KEYS)
def test_a_profile_specification_shows_its_profile_schema_and_its_overview(key):
    text = read(f"{key}-profile.md")
    definition = DEFINITIONS.profiles[key]
    shown = json.loads(re.search(r"<!-- profile-schema -->\n```json\n(.*?)```", text, re.DOTALL).group(1))

    assert shown == definition.schema == json.loads((SPEC / f"{key}-profile.schema.json").read_text(encoding="utf-8"))
    overview = table(text)
    assert (overview["Name"], overview["Version"], overview["RPP version"]) == (definition.name, definition.version, definition.rpp_version)
    assert overview["Identifier"] == f"`{definition.id}`"
    assert overview["Profile Schema `$id`"] == f"<{definition.schema['$id']}>"
    assert overview["Specification"] == f"<{definition.url}>"
    assert overview["Base profiles"] == (", ".join(f"`{b.id}` {b.version}" for b in definition.base_profiles) or "None")
    assert overview["Required extensions"] == ", ".join(f"`{r.id}` {r.version}" for r in definition.required_extensions)


@pytest.mark.parametrize("key", PROFILE_KEYS)
def test_a_profile_specification_has_a_violating_example_for_each_constrained_definition(key):
    found = examples(read(f"{key}-profile.md"))
    constrained = {target.split("#/$defs/")[1] for target in DEFINITIONS.profiles[key].schema["rpp:constraints"]
                   if target.startswith("https://github.com") and "planets-extension" in target}

    assert {name for kind, name, _ in found if kind == "violates"} >= constrained & {"planet.create", "planet.update", "satellite.create"}
    assert any(kind == "valid" for kind, _, _ in found)


@pytest.mark.parametrize("key", PROFILE_KEYS)
def test_a_valid_example_passes_with_and_without_the_profile_and_a_violating_one_only_without(key):
    without, with_ = scopes(key)

    for kind, name, example in examples(read(f"{key}-profile.md")):
        without.validate_request(name, example)         # both pass the preset schema and the profiles of the preset (none)
        if kind == "valid":
            with_.validate_request(name, example)
        else:
            with pytest.raises(ProfileConstraintViolation) as refused:
                with_.validate_request(name, example)
            assert refused.value.profile == DEFINITIONS.profiles[key].id      # the profile of the document refuses it


# --- presets

PRESET_KEYS = ("planets", "planets-atmosphere", "planets-orbits", "planets-complete", "catalogued-planets", "habitable-worlds")


def listed(cell):
    return [] if cell == "None" else re.findall(r"`([^`]+)` (\S+?)(?:,|$)", cell)


@pytest.mark.parametrize("key", PRESET_KEYS)
def test_a_preset_specification_states_the_definition_the_proxy_registers(key):
    text = read(f"{key}-preset.md")
    definition = DEFINITIONS.presets[key]
    overview = table(text)

    assert (overview["Name"], overview["Version"], overview["RPP version"]) == (definition.name, definition.version, definition.rpp_version)
    assert overview["Identifier"] == f"`{definition.id}`"
    assert overview["Specification"] == f"<{definition.url}>"
    assert listed(overview["Extensions"]) == [(r.id, r.version) for r in definition.extensions]
    assert listed(overview["Profiles"]) == [(r.id, r.version) for r in definition.profiles]
    assert listed(overview["Base presets"]) == [(r.id, r.version) for r in definition.base_presets]
    assert f"RPP-Preset: preset={definition.id};version={definition.version}" in text


def test_every_definition_the_demo_registers_has_a_specification():
    registered = {key for key in DEFINITIONS.presets if key in PRESET_KEYS}

    assert registered == set(PRESET_KEYS)
    assert {key for key in DEFINITIONS.profiles if key in PROFILE_KEYS} == set(PROFILE_KEYS)
    assert all((DEMO / f"{key}-preset.md").exists() for key in PRESET_KEYS)
    assert all((DEMO / f"{key}-profile.md").exists() for key in PROFILE_KEYS)


def test_the_specifications_are_ascii_and_have_a_changes_history():
    for path in DEMO.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        assert text.isascii(), path.name
        assert "# Changes History" in text, path.name
