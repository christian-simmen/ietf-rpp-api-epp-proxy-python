"""The rule of json §Extension Framework: an extension only adds. A sub-schema of an Extension Schema MUST NOT declare a
property that the base definition declares, list under `required` a property it does not declare, or use a keyword that
constrains the base object as a whole."""
from rpp.schema.effective_schema import bundle_definitions
from rpp.schema.profile_schema_walk import expand
from rpp.schema.rpp_extension import RppExtension

WHOLE_OBJECT = ("maxProperties", "minProperties", "not", "if", "dependentRequired", "dependentSchemas")


def check_additive(extension: RppExtension) -> None:
    base = bundle_definitions()
    for base_name, ext_name in extension.extends.items():
        sub = extension.defs[ext_name]
        label = f"The extension {extension.id}, definition {ext_name}"
        declared = {name for schema in expand([base[base_name]], base) for name in schema.get("properties", {})}
        clash = sorted(set(sub.get("properties", {})) & declared)
        if clash:
            raise ValueError(f"{label} declares {', '.join(clash)}, which {base_name} declares")
        missing = sorted(set(sub.get("required", [])) - set(sub.get("properties", {})))
        if missing:
            raise ValueError(f"{label} requires {', '.join(missing)}, which it does not declare")
        used = sorted(keyword for keyword in WHOLE_OBJECT if keyword in sub)
        if used:
            raise ValueError(f"{label} uses {', '.join(used)}, which constrains {base_name} as a whole")
        if "rpp:constraints" in sub:
            raise ValueError(f"{label} contains rpp:constraints")
