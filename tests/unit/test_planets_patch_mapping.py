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
