"""The rule of json §Extension Framework: an extension only adds. A sub-schema of an Extension Schema MUST NOT declare a
property that the base definition declares, list under `required` a property it does not declare, or use a keyword that
constrains the base object as a whole. The applicators (`allOf`, `anyOf`, `oneOf`, `then`, `else`, `dependentSchemas`) are
walked: a branch that names a member the sub-schema does not declare at its top level constrains the base object."""
from rpp.schema.bundle_definitions import bundle_definitions
from rpp.schema.profile_schema_walk import expand
from rpp.schema.rpp_extension import RppExtension

WHOLE_OBJECT = ("maxProperties", "minProperties", "not", "if", "dependentRequired", "propertyNames", "patternProperties")
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
        closed = sorted(keyword for keyword in _OPEN_KEYWORDS if sub.get(keyword, True) is not True)
        if closed:
            raise ValueError(f"{label} uses {', '.join(closed)}, which constrains {base_name} as a whole")
        if "rpp:constraints" in sub:
            raise ValueError(f"{label} contains rpp:constraints")
        for branch in _branches(sub):
            named = sorted((set(branch.get("properties", {})) | set(branch.get("required", []))) - own)
            if named:
                raise ValueError(f"{label} has a branch that names {', '.join(named)}, which it does not declare, "
                                 f"so it constrains {base_name}")
            used = sorted(keyword for keyword in (*WHOLE_OBJECT, *_OPEN_KEYWORDS) if keyword in branch)
            if used:
                raise ValueError(f"{label} has a branch that uses {', '.join(used)}, which constrains {base_name} as a whole")
