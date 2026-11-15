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

JSON = "application/json"


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


def _weight(ranges, target: str) -> Decimal:
    """The weight an `Accept` gives a media type: that of the most specific range that covers it (RFC 9110 §12.5.1), 0 where
    none does."""
    matching = [(3 if item.kind == target else 2 if item.kind == "application/*" else 1, item.quality)
                for item in ranges if item.kind in (target, "application/*", "*/*")]
    return max(matching)[1] if matching else Decimal(0)


def accepts_schema(accept_values: list[str]) -> bool:
    """Whether an `Accept` allows the document, which is `application/schema+json` and also `application/json`: absent does,
    else one of the two has a weight above 0. Parameters are ignored. Raises `MediaRangeError` for a value that does not
    parse."""
    ranges = media_range.parse_accept(accept_values)
    return not ranges or _weight(ranges, MEDIA_TYPE) > 0 or _weight(ranges, JSON) > 0
