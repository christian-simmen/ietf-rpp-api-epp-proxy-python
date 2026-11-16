"""The rule of json §Profile Schema: a sub-schema of a Profile Schema MUST NOT declare under `properties`, at any depth, a
property that the constrained definition does not declare at that depth. A property is declared by `properties`, and a
member that a schema, `patternProperties`, `additionalProperties` or `unevaluatedProperties`, covers is declared by it."""
import re

_APPLY_ALL = ("allOf", "anyOf", "oneOf")
_ITEMS = ("items", "contains")
_OPEN = ("additionalProperties", "unevaluatedProperties")


def _definition(ref: str, defs: dict):
    return defs[ref.rsplit("/", 1)[-1]] if ref.startswith("#/$defs/") else {}


def expand(schemas, defs: dict, seen=frozenset()) -> list[dict]:
    """The schemas that apply to the same instance: each one with the branches it composes and the schemas it refers to."""
    out = []
    for schema in schemas:
        if not isinstance(schema, dict) or id(schema) in seen:
            continue
        out.append(schema)
        nested = [_definition(schema["$ref"], defs)] if "$ref" in schema else []
        for keyword in _APPLY_ALL:
            nested.extend(schema.get(keyword) or ())
        nested.extend(schema[key] for key in ("then", "else") if key in schema)
        out.extend(expand(nested, defs, seen | {id(schema)}))
    return out


def _children(targets: list[dict], name: str) -> list[dict] | None:
    """The schemas that apply to the member `name` of an instance the targets describe, None where none declares it."""
    declared = [t["properties"][name] for t in targets if name in t.get("properties", {})]
    if declared:
        return declared
    covering = [schema for t in targets for pattern, schema in t.get("patternProperties", {}).items()
                if re.search(pattern, name)]
    covering += [t[key] for t in targets for key in _OPEN if isinstance(t.get(key), dict)]
    return covering or None


def _all_members(targets: list[dict]) -> list[dict]:
    """The schemas of every member: of a map, whose keys the Profile Schema names by `additionalProperties`."""
    members = [schema for t in targets for schema in t.get("properties", {}).values()]
    members += [schema for t in targets for schema in t.get("patternProperties", {}).values()]
    members += [t[key] for t in targets for key in _OPEN if isinstance(t.get(key), dict)]
    return members


def undeclared(profile_sub, profile_defs: dict, target, target_defs: dict, path: str = "$",
               visited: frozenset = frozenset()) -> list[str]:
    """The paths at which `profile_sub` declares a property the target does not. `profile_defs` are the `$defs` of the
    Profile Schema and `target_defs` those of the schema the target is in."""
    if not isinstance(profile_sub, dict):
        return []
    targets = expand([target] if isinstance(target, dict) else target, target_defs)
    key = (id(profile_sub), tuple(sorted(id(t) for t in targets)))
    if key in visited:
        return []
    visited = visited | {key}
    found = []
    for branch in expand([profile_sub], profile_defs):
        for name, sub in branch.get("properties", {}).items():
            children = _children(targets, name)
            if children is None:
                found.append(f"{path}.{name}")
            else:
                found += undeclared(sub, profile_defs, children, target_defs, f"{path}.{name}", visited)
        for keyword in _ITEMS:
            if isinstance(branch.get(keyword), dict):
                children = [t[keyword] for t in targets if isinstance(t.get(keyword), dict)]
                found += undeclared(branch[keyword], profile_defs, children, target_defs, f"{path}[]", visited)
        for keyword in ("additionalProperties", "unevaluatedProperties"):
            if isinstance(branch.get(keyword), dict):
                found += undeclared(branch[keyword], profile_defs, _all_members(targets), target_defs, f"{path}.*", visited)
    return found
