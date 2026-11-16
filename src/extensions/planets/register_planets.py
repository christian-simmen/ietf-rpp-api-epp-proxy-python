import json
from pathlib import Path

from extensions.planets.core.ports.planets_gateways import EXTENSION_ID
from extensions.planets.rpp.schema.openapi_fragment import HANDLERS, openapi_fragment
from registration import ExtensionRegistry, RegisteredExtension

SCHEMA = Path(__file__).parent / "rpp" / "schema" / "planets-extension.schema.json"

# The top-level data elements of the objects, with their Visibility (docs/demo/planets-extension.md).
DATA_OBJECTS = {
    "planet": {"id": "default", "provMetadata": "default", "type": "default", "radius": "default", "mass": "default",
               "authInfo": "default", "satellite": "onDemand", "processes": "default"},
    "satellite": {"id": "default", "provMetadata": "default", "planet": "default", "orbitalPeriod": "default"},
}

TRANSFER_OPERATIONS = ["request", "query", "cancel", "approve", "reject"]

PRESET_KEY = "planets"


def register(registry: ExtensionRegistry) -> None:
    """Registers every part of the extension in the pipeline: its schema, the data model, the OpenAPI fragment and the
    handlers of its paths, its objects, its part of the SQLite backend, the leaves it adds to the backend profile, and the
    RPP preset that offers it."""
    registry.add(RegisteredExtension(
        id=EXTENSION_ID,
        schema=json.loads(SCHEMA.read_text(encoding="utf-8")),
        data_objects=DATA_OBJECTS,
        objects=("planet", "satellite"),
        openapi=openapi_fragment,
        handlers=HANDLERS,
        backend_parts={"sqlite": "registry_adapter.sqlite.extensions.planets"},
        profile_layer={
            "objects": ["planet", "satellite"],
            "extensions": [EXTENSION_ID],
            "planet": {"processes": {"transfer": {"operations": TRANSFER_OPERATIONS}}},
        },
        profile_leaves={"planet.processes.transfer.operations": tuple},
        presets={PRESET_KEY: {
            "id": "org.example.rpp.preset.planets",
            "name": "Planets preset",
            "description": "Demo preset of the planets extension: the planets and satellites of the SQLite backend",
            "version": "1.0",
            "rppVersion": "1.0",
            "basePresets": [{"id": "urn:ietf:params:rpp:preset:base", "version": "1.0"}],
            "extensions": [{"id": EXTENSION_ID, "version": "1.0"}],
            "profiles": [],
        }},
    ))
