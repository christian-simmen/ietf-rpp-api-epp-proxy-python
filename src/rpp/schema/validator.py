import re

import jsonschema
from jsonschema import Draft202012Validator

from rpp.schema.effective_schema import UNEVALUATED, bundle_definitions, effective_definitions
from rpp.schema.extensions import EXTENSIONS, own_definitions

# The effective validators of json §7.2, by definition and the extensions it is composed with, on the combined schema
# of `effective_schema.py`. `build_effective` fills them for every definition of one extension tuple, once, when the app
# is built; a request only looks one up.
_effective: dict[tuple[str, tuple[str, ...]], Draft202012Validator | None] = {}

_UNEXPECTED = re.compile(r"\((.*) (?:was|were) unexpected\)")


def _target(name: str, definitions: dict) -> str | None:
    """The definition of the combined schema that `name` stands for: an extension's own object (`requestContact.create`)
    is validated by the name a base object's would have."""
    if name in definitions:
        return name
    own = own_definitions().get(name)
    return own if own in definitions else None


def _names() -> set[str]:
    return {*bundle_definitions(), *own_definitions()}


def _compose(schema_name: str, extensions: tuple[str, ...]):
    """The validator of a definition of the combined schema of the extensions; None where it has none."""
    definitions = effective_definitions(extensions)
    target = _target(schema_name, definitions)
    if target is None:
        return None
    return Draft202012Validator({"$ref": f"#/$defs/{target}", "$defs": definitions})


def build_effective(extensions: tuple[str, ...]) -> None:
    """Builds the validator of every definition the extensions of a profile give, unless it was built before."""
    extensions = tuple(extensions)
    for name in _names():
        if (name, extensions) not in _effective:
            _effective[(name, extensions)] = _compose(name, extensions)    # None: the profile has no such definition


def effective_validator(schema_name: str, extensions: tuple[str, ...]):
    """The validator of a definition for the extensions of a profile. One the profile does not have (an extension's own
    object under a profile without the extension: only a test that maps without an app reaches it) is the combined
    schema of every extension's. A tuple the app did not build is built on first use."""
    extensions = tuple(extensions)
    key = (schema_name, extensions)
    if key not in _effective:
        build_effective(extensions)
    if _effective[key] is None:
        everything = tuple(EXTENSIONS)
        build_effective(everything)
        key = (schema_name, everything)
    return _effective[key]


def validate_schema(schema_name, data, extensions: tuple[str, ...] = ()):
    """Validates `data` against a definition of the combined schema of the given extensions. A member no schema declares
    is refused as an undeclared property (json §4.9.1), the same `ValueError` the dataclasses' check raises."""
    try:
        effective_validator(schema_name, tuple(extensions)).validate(data)
    except jsonschema.ValidationError as error:
        if error.validator == UNEVALUATED:
            names = _UNEXPECTED.search(error.message)
            raise ValueError(f"Undeclared property: {names.group(1) if names else error.message}") from None
        raise
