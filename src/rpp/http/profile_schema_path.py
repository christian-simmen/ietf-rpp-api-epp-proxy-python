"""The path `/profiles/{name}/schema`, which publishes the effective schema of a profile (docs/profile-schemas-extension.md).
The drafts define none, so it is made from the path of the Profile Data Object, as the paths of an extension's objects
are made from a base object's (`extension_paths.py`): same parameters and errors, no security, a JSON Schema as its answer."""
import copy

from rpp.schema.profile_schemas import MEDIA_TYPE

PROFILE_PATH = "/profiles/{name}"
SCHEMA_PATH = PROFILE_PATH + "/schema"
RPP_MEDIA_TYPE = "application/rpp+json"


def add_profile_schema_path(spec: dict) -> dict:
    path = copy.deepcopy(spec["paths"][PROFILE_PATH])
    operation = path["get"]
    operation["operationId"] = "profiles_schemaRead"
    operation["security"] = []     # public, as discovery is
    operation["description"] = ("The effective JSON Schema of the profile (json §7.2): the data definitions and those of the "
                                "profile's extensions. It is the schema the server validates with.")
    content = operation["responses"]["200"]["content"]
    content[MEDIA_TYPE] = {"schema": {"type": "object"}}
    del content[RPP_MEDIA_TYPE]
    spec["paths"][SCHEMA_PATH] = path
    return spec
