"""The rule of json §Extension Framework: an extension only adds. A sub-schema of an Extension Schema MUST NOT declare a
property that the base definition declares, list under `required` a property it does not declare, or use a keyword that
constrains the base object as a whole. The applicators (`allOf`, `anyOf`, `oneOf`, `then`, `else`, `dependentSchemas`) are
walked: a branch that names a member the sub-schema does not declare at its top level constrains the base object."""
import re

from rpp.schema.bundle_definitions import bundle_definitions
from rpp.schema.profile_schema_walk import expand
from rpp.schema.rpp_extension import RppExtension

# Keywords that constrain the base object whatever they name; those that name members are checked by what they name.
WHOLE_OBJECT = ("maxProperties", "minProperties", "propertyNames")
_NAMING = ("not", "if", "dependentRequired", "dependentSchemas")
_OPEN_KEYWORDS = ("additionalProperties", "unevaluatedProperties")
_APPLICATORS = ("allOf", "anyOf", "oneOf")


def _branches(sub: dict):
    """The schemas an applicator of `sub` holds, at any depth."""
    for keyword in _APPLICATORS:
        for branch in sub.get(keyword) or ():
            yield branch
            yield from _branches(branch)
    for keyword in ("then", "else"):
        if isinstance(sub.get(keyword), dict):
            yield sub[keyword]
            yield from _branches(sub[keyword])
    for branch in (sub.get("dependentSchemas") or {}).values():
        yield branch
        yield from _branches(branch)


def _named(schema: dict) -> set:
    """The members that a schema's `properties`, `required`, `dependentRequired`, `dependentSchemas`, `if`, `then`, `else` and
    `not` name, at its top level and in what they hold."""
    names = set(schema.get("properties", {})) | set(schema.get("required", []))
    for member, required in (schema.get("dependentRequired") or {}).items():
        names |= {member, *required}
    for member, branch in (schema.get("dependentSchemas") or {}).items():
        names |= {member} | _named(branch)
    for keyword in ("not", "if", "then", "else"):
        if isinstance(schema.get(keyword), dict):
            names |= _named(schema[keyword])
    return names


def check_additive(extension: RppExtension) -> None:
    base = bundle_definitions()
    for base_name, ext_name in extension.extends.items():
        sub = extension.defs[ext_name]
        label = f"The extension {extension.id}, definition {ext_name}"
        declared = {name for schema in expand([base[base_name]], base) for name in schema.get("properties", {})}
        own = set(sub.get("properties", {}))
        clash = sorted(own & declared)
        if clash:
            raise ValueError(f"{label} declares {', '.join(clash)}, which {base_name} declares")
        missing = sorted(set(sub.get("required", [])) - own)
        if missing:
            raise ValueError(f"{label} requires {', '.join(missing)}, which it does not declare")
        used = sorted(keyword for keyword in WHOLE_OBJECT if keyword in sub)
        if used:
            raise ValueError(f"{label} uses {', '.join(used)}, which constrains {base_name} as a whole")
        for pattern in sub.get("patternProperties") or {}:
            hit = sorted(name for name in declared if re.search(pattern, name))
            if hit:
                raise ValueError(f"{label} has a patternProperties {pattern!r} that matches {', '.join(hit)}, "
                                 f"which {base_name} declares")
        closed = sorted(keyword for keyword in _OPEN_KEYWORDS if sub.get(keyword, True) is not True)
        if closed:
            raise ValueError(f"{label} uses {', '.join(closed)}, which constrains {base_name} as a whole")
        if "rpp:constraints" in sub:
            raise ValueError(f"{label} contains rpp:constraints")
        for schema in (sub, *_branches(sub)):
            named = _named(schema) - own
            if named:
                raise ValueError(f"{label} has a branch that names {', '.join(sorted(named))}, which it does not declare, "
                                 f"so it constrains {base_name}")
        for branch in _branches(sub):
            used = sorted(keyword for keyword in (*WHOLE_OBJECT, *_OPEN_KEYWORDS) if keyword in branch)
            if used:
                raise ValueError(f"{label} has a branch that uses {', '.join(used)}, which constrains {base_name} as a whole")
