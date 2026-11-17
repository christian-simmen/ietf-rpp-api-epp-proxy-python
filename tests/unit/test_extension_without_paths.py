"""An extension that adds members only (no data object, no path) registers no handlers and no OpenAPI fragment (#179)."""
from registration import ExtensionRegistry, RegisteredExtension
from rpp.http.extension_paths import add_registered_paths


def test_an_extension_without_handlers_and_openapi_adds_no_package_and_no_path():
    registry = ExtensionRegistry()
    registry.add(RegisteredExtension(
        id="org.example.rpp.extension.members", schema={}, data_objects={}, objects=()))
    spec = {"paths": {"/x": {}}, "components": {"schemas": {}}}

    assert registry.handler_packages() == ()
    assert add_registered_paths(spec, registry) == {"paths": {"/x": {}}, "components": {"schemas": {}}}
