"""The partial update of json §5.2 is translated into core change sets in `rpp/mapping`: what goes on holds no JSON, and a
value is checked against the update schema first."""
import pytest
from jsonschema import ValidationError

from extensions.planets.core.model.planet_changes import PlanetChanges
from extensions.planets.core.model.satellite_changes import SatelliteChanges
from extensions.planets.rpp.mapping import planet_patch, satellite_patch
from rpp.schema.extensions import register_extension

import json
from pathlib import Path

pytestmark = pytest.mark.lazy_schemas

SCHEMA = json.loads((Path(__file__).parents[2] / ".spec" / "planets-extension.schema.json").read_text(encoding="utf-8"))
register_extension(SCHEMA)
EXTENSIONS = (SCHEMA["rpp:extension"]["id"],)


def planet(*operations):
    return planet_patch.rpp_to_model(list(operations), EXTENSIONS)


def test_add_and_replace_set_a_member_and_remove_clears_it():
    changes = planet({"op": "replace", "path": "/radius", "value": 10}, {"op": "add", "path": "/type", "value": "gas-giant"},
                     {"op": "remove", "path": "/mass"})

    assert changes == PlanetChanges(type="gas-giant", radius=10, cleared=frozenset({"mass"}))


def test_the_last_operation_on_a_member_wins():
    assert planet({"op": "remove", "path": "/radius"}, {"op": "add", "path": "/radius", "value": 2}) == PlanetChanges(radius=2)
    assert planet({"op": "add", "path": "/radius", "value": 2}, {"op": "remove", "path": "/radius"}) == PlanetChanges(
        cleared=frozenset({"radius"}))


def test_the_auth_info_becomes_a_core_auth_info():
    changes = planet({"op": "replace", "path": "/authInfo",
                      "value": {"@type": "authInfo", "method": "authinfo", "authdata": "Word-1"}})

    assert changes.authInfo.pw == "Word-1"


@pytest.mark.parametrize("operation", [
    {"op": "remove", "path": "/type"}, {"op": "remove", "path": "/authInfo"}, {"op": "replace", "path": "/id", "value": "x"},
    {"op": "move", "path": "/radius", "value": 1}, {"op": "replace", "path": "/radius"},
    {"op": "replace", "path": "/radius", "value": 1, "match": {"a": 1}}, {"op": "replace", "path": "/provMetadata", "value": {}},
])
def test_what_cannot_change_is_refused(operation):
    with pytest.raises(ValueError):
        planet(operation)


@pytest.mark.parametrize("operation", [
    {"op": "replace", "path": "/type", "value": "moonlike"}, {"op": "replace", "path": "/radius", "value": -1},
    {"op": "replace", "path": "/mass", "value": "heavy"},
    {"op": "replace", "path": "/authInfo", "value": {"method": "authinfo"}},
])
def test_a_value_the_update_schema_refuses_is_refused(operation):
    with pytest.raises(ValidationError):
        planet(operation)


def test_a_satellite_patch_sets_or_clears_the_orbital_period():
    assert satellite_patch.rpp_to_model([{"op": "replace", "path": "/orbitalPeriod", "value": 2}], EXTENSIONS) == \
        SatelliteChanges(orbitalPeriod=2)
    assert satellite_patch.rpp_to_model([{"op": "remove", "path": "/orbitalPeriod"}], EXTENSIONS) == \
        SatelliteChanges(cleared=frozenset({"orbitalPeriod"}))
    for operation in ({"op": "replace", "path": "/planet", "value": {}}, {"op": "replace", "path": "/orbitalPeriod", "value": 0}):
        with pytest.raises((ValueError, ValidationError)):
            satellite_patch.rpp_to_model([operation], EXTENSIONS)


# A native patch has no read (D24), so a profile is checked on the value of each operation as the member it sets, and the
# removal of a member a profile requires is refused. What a profile requires of the members together is not enforced.
from rpp.schema import request_schemas  # noqa: E402
from rpp.schema.extensions import EXTENSIONS as KNOWN  # noqa: E402
from rpp.schema.offered_presets import OfferedPresets  # noqa: E402
from rpp.schema.profile_constraint_violation import ProfileConstraintViolation  # noqa: E402
from rpp.schema.schema_scope import SchemaScope  # noqa: E402
from tests.helper.preset_fixtures import BASE, definitions_with, preset, profile  # noqa: E402

PLANETS = SCHEMA["rpp:extension"]["id"]
BIG = profile("big-planets", required=[(PLANETS, "1.0")], constraints={}, defs={
    "profile.big": {"properties": {"radius": {"minimum": 1000}}, "required": ["mass"]}})
BIG[1]["schema"]["rpp:constraints"] = {f"{KNOWN[PLANETS].url}#/$defs/planet.update": "#/$defs/profile.big"}


@pytest.fixture
def under_big_planets():
    entry = preset("planets", base_presets=[BASE["id"]], extensions=[(PLANETS, "1.0")], profiles=[BIG[0]])
    offered = OfferedPresets.build(definitions_with([entry], [BIG]), ["planets"], "planets", {}, (PLANETS,)).offered[0]
    scope = SchemaScope(offered.extensions, offered.applicable, offered.required)
    token = request_schemas.use(request_schemas.RequestSchemas(request=scope, response=scope, scopes=(scope,)))
    yield
    request_schemas.release(token)


def test_the_value_of_an_operation_is_checked_against_the_profile_as_the_member_it_sets(under_big_planets):
    with pytest.raises(ProfileConstraintViolation) as error:
        planet({"op": "replace", "path": "/radius", "value": 10})

    assert error.value.profile == BIG[0] and error.value.path == "$.radius"
    assert planet({"op": "replace", "path": "/radius", "value": 5000}).radius == 5000


def test_a_member_the_profile_requires_is_not_missing_from_a_single_operation(under_big_planets):
    # `mass` is required by the profile, but a patch of the type alone does not make it absent: cross-member constraints are
    # not enforced on a native patch
    assert planet({"op": "replace", "path": "/type", "value": "rocky"}).type == "rocky"


def test_the_removal_of_a_member_the_profile_requires_is_refused_naming_the_profile(under_big_planets):
    with pytest.raises(ProfileConstraintViolation) as error:
        planet({"op": "remove", "path": "/mass"})

    assert error.value.profile == BIG[0] and error.value.path == "$.mass"
    assert planet({"op": "remove", "path": "/radius"}).cleared == frozenset({"radius"})      # not required
