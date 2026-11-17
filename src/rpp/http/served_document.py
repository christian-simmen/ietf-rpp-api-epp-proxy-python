"""The OpenAPI document a deployment serves (#204): OpenAPI 3.1, made when the app is built from the spec Connexion routes with
(OpenAPI 3.0, which Connexion requires), with the body schemas of the default preset's Preset Schema (json §Preset Schema), the
same as `GET /presets/{id}/schema` publishes it: the members of its extensions and the constraints of its applicable profiles.

The definitions of the Preset Schema go under `components/schemas` by their keys, their references rewritten from `#/$defs/` to
there. A body marked with the definition it stands for (`body_definitions`) points at the preset's definition, an extension's own
object at the key the extension gives it (`own_definitions`); a body of no definition, or of one the preset does not have (an
object of an extension of another preset), keeps its schema. A schema of the routing spec that nothing refers to
any more is left out; the definitions of the Preset Schema all stay, as it publishes them."""
import copy
import json

from rpp.http.body_definitions import MARKER, body_schemas
from rpp.schema.extensions import own_definitions

OPENAPI_VERSION = "3.1.0"
SCHEMAS = "#/components/schemas/"
_DEFS = '"#/$defs/'


def _in_components(defs: dict) -> dict:
    return json.loads(json.dumps(defs).replace(_DEFS, f'"{SCHEMAS}'))


def _references(node, found: set) -> None:
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith(SCHEMAS):
            found.add(ref[len(SCHEMAS):])
        for value in node.values():
            _references(value, found)
    elif isinstance(node, list):
        for value in node:
            _references(value, found)


def _referenced_schemas(document: dict) -> set:
    """The component schemas the document refers to, from outside `components/schemas` and then from those, transitively."""
    schemas = document["components"]["schemas"]
    found = set()
    _references({key: value for key, value in document.items() if key != "components"}, found)
    _references({key: value for key, value in document["components"].items() if key != "schemas"}, found)
    pending = list(found)
    while pending:
        inner = set()
        _references(schemas.get(pending.pop()), inner)
        for name in inner - found:
            found.add(name)
            pending.append(name)
    return found


def served_document(spec: dict, preset_document: dict, extension_ids) -> dict:
    """The document to serve, from the routing spec (with its bodies marked) and the default preset's Preset Schema; the
    extensions are those of the preset. A component the routing spec has under a key of the Preset Schema with other content
    is a defect of the app, not of a request: it stops the app."""
    document = copy.deepcopy(spec)
    defs = preset_document["$defs"]
    own = own_definitions(extension_ids)
    for schema in body_schemas(document):
        name = schema.pop(MARKER, None)
        key = name if name in defs else own.get(name)
        if key in defs:
            schema.clear()
            schema["$ref"] = SCHEMAS + key
    schemas = document["components"]["schemas"]
    for key, schema in _in_components(defs).items():
        if key in schemas and schemas[key] != schema:
            raise ValueError(f"The OpenAPI document has a schema {key} that differs from the definition of the preset")
        schemas[key] = schema
    referenced = _referenced_schemas(document)
    for name in list(schemas):
        if name not in referenced and name not in defs:
            del schemas[name]
    document["openapi"] = OPENAPI_VERSION
    document["info"]["x-rpp-preset"] = dict(preset_document["rpp:preset"])
    return document
