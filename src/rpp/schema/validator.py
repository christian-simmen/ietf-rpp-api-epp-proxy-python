import json
import os

from jsonschema import Draft202012Validator

from rpp.schema.extensions import EXTENSIONS, own_definitions

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), 'schemas', 'rpp.schema.normalized.json')

with open(SCHEMA_FILE) as f:
    _bundle = json.load(f)

# The definitions of the bundle and of every extension: an extension's names start with `ext.` (json §7).
_defs = {**_bundle["$defs"], **{name: schema for extension in EXTENSIONS.values()
                                 for name, schema in extension.defs.items()}}


def bundle_definitions() -> dict:
    """The definitions of the bundle, which the drafts generate; the extensions' are not among them."""
    return _bundle["$defs"]


def _validator_for(schema_name):
    return Draft202012Validator({"$ref": f"#/$defs/{schema_name}", "$defs": _defs})


validators = {name: _validator_for(name) for name in _bundle["$defs"]}

# An extension's own objects (`requestContact.create`), validated by the names a base object's would have.
validators.update({name: _validator_for(definition) for name, definition in own_definitions().items()
                   if name not in validators})


# The effective validators of json §7.2, by definition and the extensions it is composed with. `build_effective` fills
# them for every definition of one extension tuple, once, when the app is built; a request only looks one up.
_effective: dict[tuple[str, tuple[str, ...]], Draft202012Validator] = {}


def _compose(schema_name: str, extensions: tuple[str, ...]):
    """The effective schema of json §7.2: the base definition and those the extensions add to it, with `allOf`."""
    added = [EXTENSIONS[extension].extends.get(schema_name) for extension in extensions]
    parts = [{"$ref": f"#/$defs/{name}"} for name in [schema_name, *added] if name]
    if len(parts) == 1:
        return validators[schema_name]
    return Draft202012Validator({"allOf": parts, "$defs": _defs})


def build_effective(extensions: tuple[str, ...]) -> None:
    """Builds the validator of every definition for the extensions of a profile, unless it was built before."""
    extensions = tuple(extensions)
    for name in validators:
        if (name, extensions) not in _effective:
            _effective[(name, extensions)] = _compose(name, extensions)


def effective_validator(schema_name: str, extensions: tuple[str, ...]):
    """The validator of a definition for the extensions of a profile. A tuple the app did not build (a test that
    maps without an app) is built on first use."""
    extensions = tuple(extensions)
    try:
        return _effective[(schema_name, extensions)]
    except KeyError:
        build_effective(extensions)
        return _effective[(schema_name, extensions)]


def validate_schema(schema_name, data, extensions: tuple[str, ...] = ()):
    """Validates `data` against a definition of the bundle, composed with what the given extensions add to it."""
    effective_validator(schema_name, tuple(extensions)).validate(data)
