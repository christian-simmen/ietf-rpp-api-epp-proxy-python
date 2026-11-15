"""The path `/profiles/{name}/schema`, which publishes the effective schema of a profile (docs/profile-schemas-extension.md).
The drafts define none, so it is made from the path of the Profile Data Object, as the paths of an extension's objects
are made from a base object's (`extension_paths.py`): same errors and path parameter, no security. It is a fetch of a
JSON Schema document, not an RPP operation: it is outside profile signalling (`ProfileMiddleware`), and a generic JSON
Schema client that resolves the `$id` sends neither `RPP-Cltrid` nor an RPP `Accept`, so both are optional here."""
import copy
from decimal import Decimal

from rpp.http import media_range
from rpp.schema.profile_schemas import MEDIA_TYPE

PROFILE_PATH = "/profiles/{name}"
SCHEMA_PATH = PROFILE_PATH + "/schema"
RPP_MEDIA_TYPE = "application/rpp+json"
OPERATION = "profiles_schemaRead"

# What an `Accept` may name for the document, by how specific it is (RFC 9110 §12.5.1).
_ACCEPTED = {MEDIA_TYPE: 3, "application/json": 3, "application/*": 2, "*/*": 1}


def _header(name: str, description: str) -> dict:
    return {"name": name, "in": "header", "required": False, "description": description, "schema": {"type": "string"}}


def add_profile_schema_path(spec: dict) -> dict:
    path = copy.deepcopy(spec["paths"][PROFILE_PATH])
    operation = path["get"]
    operation["operationId"] = OPERATION
    operation["security"] = []     # public, as discovery is
    operation["description"] = ("The effective JSON Schema of the profile (json §7.2): the data definitions and those of the "
                                "profile's extensions. It is the schema the server validates with.")
    operation["parameters"] = [
        operation["parameters"][0],
        _header("RPP-Cltrid", "Optional here: a client that resolves the `$id` of the schema need not send one."),
        _header("Accept", f"`{MEDIA_TYPE}`, `application/json`, `application/*` or `*/*`; absent is any."),
    ]
    ok = operation["responses"]["200"]
    ok["headers"]["RPP-Cltrid"]["required"] = False      # echoed when the request had one
    ok["headers"]["Vary"] = {"required": False, "schema": {"type": "string"}}
    content = ok["content"]
    content[MEDIA_TYPE] = {"schema": {"type": "object"}}
    del content[RPP_MEDIA_TYPE]
    spec["paths"][SCHEMA_PATH] = path
    return spec


def accepts_schema(accept_values: list[str]) -> bool:
    """Whether an `Accept` allows the document: absent does, else the most specific range that names `application/schema+json`
    or `application/json`, or the wildcards that cover them, is not weighted 0. Parameters are ignored. Raises
    `MediaRangeError` for a value that does not parse."""
    ranges = media_range.parse_accept(accept_values)
    if not ranges:
        return True
    matches = [(_ACCEPTED[item.kind], item.quality) for item in ranges if item.kind in _ACCEPTED]
    return bool(matches) and max(matches)[1] > Decimal(0)
