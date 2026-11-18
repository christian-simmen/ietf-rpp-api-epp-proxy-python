from registration import ExtensionRegistry, RegisteredExtension


def register_definitions(registry: ExtensionRegistry, name: str, presets=(), profiles=()) -> None:
    """Registers an extension that brings only presets and profiles (`(identifier, definition)` pairs of
    `tests/helper/preset_fixtures.py`): no data object and no path, and a SQLite part without tables (the backend holds only extensions that have a part)."""
    identifier = f"org.example.rpp.extension.{name}"
    registry.add(RegisteredExtension(
        id=identifier,
        schema={"$id": f"https://example.org/{name}", "rpp:extension": {"id": identifier, "name": name, "version": "1.0"},
                "rpp:extends": {}, "$defs": {}},
        data_objects={}, objects=(), backend_parts={"sqlite": "tests.refused_configs.definitions_sqlite_part"},
        presets={key.rsplit(".", 1)[1]: data for key, data in presets},
        profiles={key.rsplit(".", 1)[1]: data for key, data in profiles}))
