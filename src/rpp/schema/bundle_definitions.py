"""The definitions of the bundle of RPP, which the drafts generate (`rpp.schema.normalized.json`)."""
import json
import os

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), 'schemas', 'rpp.schema.normalized.json')

with open(SCHEMA_FILE) as f:
    _bundle = json.load(f)


def bundle_definitions() -> dict:
    """The definitions of the bundle; the extensions' are not among them."""
    return _bundle["$defs"]
