"""The combined schema of a deployment (extension guidelines §8.6): the definitions of the bundle and of the extensions of a
profile, each extended definition composed with `allOf`, and `"unevaluatedProperties": false` injected at every
object-schema node (json §4.9.1). The drafts' own documents do not have the injection; this one is both what a profile
publishes and what the proxy validates with."""
import copy
import json
import os

from rpp.schema.extensions import EXTENSIONS

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), 'schemas', 'rpp.schema.normalized.json')

with open(SCHEMA_FILE) as f:
    _bundle = json.load(f)

UNEVALUATED = "unevaluatedProperties"

# Schema keywords whose value is a schema, a list of schemas, or a map of schemas that the injection goes into.
_SCHEMA = ("items", "contains", "then", "else", "additionalProperties", "unevaluatedProperties")
_SCHEMAS = ("allOf", "anyOf", "oneOf", "prefixItems")
_SCHEMA_MAPS = ("properties", "patternProperties", "dependentSchemas", "$defs")
# `if` and `not` are conditions, not what an instance must be: an injection there would change what they match.


def bundle_definitions() -> dict:
    """The definitions of the bundle, which the drafts generate; the extensions' are not among them."""
    return _bundle["$defs"]


def _inject(node, root: bool = True) -> None:
    """Puts the keyword at every object-schema node of `node` (`type` is `object`) that says nothing about members it does
    not declare: `unevaluatedProperties` or `additionalProperties` (free keys) already there stay as they are. `root` is
    False for the node of a definition that is composed with `allOf`: the keyword goes on the composition."""
    if isinstance(node, list):
        for item in node:
            _inject(item)
        return
    if not isinstance(node, dict):
        return
    if root and node.get("type") == "object" and UNEVALUATED not in node and "additionalProperties" not in node:
        node[UNEVALUATED] = False
    for keyword in _SCHEMA:
        if isinstance(node.get(keyword), dict):
            _inject(node[keyword])
    for keyword in _SCHEMAS:
        if isinstance(node.get(keyword), list):
            for item in node[keyword]:
                _inject(item)
    for keyword in _SCHEMA_MAPS:
        if isinstance(node.get(keyword), dict):
            for value in node[keyword].values():
                _inject(value)


_effective: dict[tuple[str, ...], dict] = {}


def effective_definitions(extensions: tuple[str, ...]) -> dict:
    """The `$defs` of the combined schema of the extensions of a profile, built once per tuple. A definition an extension
    extends is the `allOf` of the base definition and the extension's, which holds the injection, so the members the
    extension adds are evaluated by the branch that declares them (the bundle references no extended definition from
    another one, so composing in place changes no other)."""
    extensions = tuple(extensions)
    if extensions in _effective:
        return _effective[extensions]
    definitions = copy.deepcopy(bundle_definitions())
    composed: dict[str, list] = {}
    branches = set()
    for extension in extensions:
        definitions.update(copy.deepcopy(EXTENSIONS[extension].defs))
        for base, ext in EXTENSIONS[extension].extends.items():
            composed.setdefault(base, []).append({"$ref": f"#/$defs/{ext}"})
            branches.add(ext)
    for name, schema in definitions.items():
        _inject(schema, root=name not in branches and name not in composed)
    for base, refs in composed.items():
        definitions[base] = {"allOf": [definitions[base], *refs], UNEVALUATED: False}
    _effective[extensions] = definitions
    return definitions
