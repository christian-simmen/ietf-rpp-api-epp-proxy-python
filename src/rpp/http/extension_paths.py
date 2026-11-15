"""The paths of the data objects an offered extension defines. Core §16.1 derives every path from an object's
Identifier (guidelines §5.7): `/requestContacts`, `/requestContacts/{id}` and `/requestContacts/{id}/availability`.
The OpenAPI document is generated from the drafts and has none of them, so they are made from the paths of the base
object whose uniform interface the extension's object shares (`TEMPLATES`), with its own operationIds. Their schemas
in the OpenAPI document are plain objects: the mappers validate with the extension's schema."""
import copy
import re

from rpp.schema.extensions import EXTENSIONS

# The base object whose create, read, update, delete and availability an extension's object has, and the paths of it
# it takes: its processes are not the extension object's.
TEMPLATES = {"requestContact": "contact"}

SUFFIXES = ("", "/{id}", "/{id}/availability")

INCLUDE_ELEMENTS = "#/components/parameters/gen.IncludeElements"

SCHEMA_REF = re.compile(r"^#/components/schemas/gen\.(\w+)(\.\w+)$")


def plural(identifier: str) -> str:
    """Core §16.1.1, for the identifiers here."""
    return f"{identifier}s"


def _renamed(node, template: str, identifier: str, schemas: dict):
    """The node of a path of the template object, for the extension's object: its operationIds and schemas renamed,
    and its descriptions left out, as they describe the template object."""
    if isinstance(node, list):
        return [_renamed(item, template, identifier, schemas) for item in node]
    if not isinstance(node, dict):
        return node
    renamed = {}
    for key, value in node.items():
        if key == "description" and isinstance(value, str) and "operationId" in node:
            continue
        if key == "operationId":
            value = value.replace(plural(template), plural(identifier), 1)
        elif key == "$ref" and isinstance(value, str):
            match = SCHEMA_REF.fullmatch(value)
            if match and match.group(1) in (template, f"{template}Availability"):
                name = f"ext.{match.group(1).replace(template, identifier, 1)}{match.group(2)}"
                schemas[name] = {"type": "object", "description": "Validated with the schema of the extension"}
                value = f"#/components/schemas/{name}"
        renamed[key] = _renamed(value, template, identifier, schemas)
    return renamed


def add_extension_paths(spec: dict, extensions) -> dict:
    """Adds to the OpenAPI document the paths of the objects the offered extensions define."""
    schemas = {}
    for extension in extensions:
        for identifier in EXTENSIONS[extension].objects:
            template = TEMPLATES[identifier]
            for suffix in SUFFIXES:
                path = copy.deepcopy(spec["paths"][f"/{plural(template)}{suffix}"])
                spec["paths"][f"/{plural(identifier)}{suffix}"] = _renamed(path, template, identifier, schemas)
    spec["components"]["schemas"].update(schemas)
    return spec
