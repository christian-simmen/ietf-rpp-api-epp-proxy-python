"""The rule of json §Extension Framework: an extension only adds. The proxy checks it with a whitelist, so that no schema that
constrains the base object can pass by a keyword the check did not think of.

The sub-schema that an Extension Schema maps to a base definition, and every sub-schema reached through `allOf`, `anyOf`,
`if`, `then`, `else` and the values of `dependentSchemas`, may only use:

- metadata: `$id`, `$schema`, `$comment`, `$defs`, `title`, `description`, `examples`, `deprecated`, and `rpp:*`;
- `type` with the value `object`;
- `properties`, whose keys the base definition does not declare (the values are free, they constrain the extension's own members);
- `required` and `dependentRequired`, naming the extension's own members only (those the sub-schema declares in its top-level
  `properties`), and `dependentSchemas` keyed by own members;
- `patternProperties`, whose patterns match no member the base definition declares;
- `additionalProperties` and `unevaluatedProperties`, absent or `true`;
- the applicators listed above, with at least one branch, and the schema `true`. `oneOf` is not one of them: branches that are
  each allowed can still exclude each other, so that no base object matches (`oneOf: [{}, {}]`).

Everything else is refused (`not`, `oneOf`, `const`, `enum`, `propertyNames`, `minProperties`, `maxProperties`, the schema `false`, an empty `allOf` or `anyOf`, ...)
naming the extension, the definition and the keyword. This is stricter than json: `not` over the extension's own members would
be additive, and is refused too, because a whitelist cannot let a schema that constrains the base slip through."""
import re

from rpp.schema.bundle_definitions import bundle_definitions
from rpp.schema.profile_schema_walk import expand
from rpp.schema.rpp_extension import RppExtension

_METADATA = ("$id", "$schema", "$comment", "$defs", "title", "description", "examples", "deprecated")
_APPLICATORS_LIST = ("allOf", "anyOf")
_APPLICATORS_SCHEMA = ("if", "then", "else")
_OPEN = ("additionalProperties", "unevaluatedProperties")


class _Check:
    def __init__(self, extension: RppExtension, definition: str, base_name: str):
        self.label = f"The extension {extension.id}, definition {definition}"
        self.base_name = base_name
        base = bundle_definitions()
        self.declared = {name for schema in expand([base[base_name]], base) for name in schema.get("properties", {})}
        self.own: set[str] = set()

    def fail(self, keyword: str, why: str):
        raise ValueError(f"{self.label} uses {keyword}, {why}")

    def run(self, sub) -> None:
        if not isinstance(sub, dict):
            self.fail("a schema that is not an object", f"which {self.base_name} cannot take as an addition")
        self.own = set(sub.get("properties", {}))
        clash = sorted(self.own & self.declared)
        if clash:
            raise ValueError(f"{self.label} declares {', '.join(clash)}, which {self.base_name} declares")
        self.node(sub, top=True)

    def node(self, node, top: bool = False) -> None:
        if node is True:
            return
        if not isinstance(node, dict):
            self.fail("the schema false" if node is False else "a schema that is not an object",
                      f"which constrains {self.base_name}")
        for keyword, value in node.items():
            if keyword in _METADATA or keyword.startswith("rpp:"):
                continue
            if keyword == "type":
                if value != "object":
                    self.fail(f"type {value!r}", f"which is not the object {self.base_name} is")
            elif keyword == "properties":
                names = set(value)
                if top and names & self.declared:
                    continue    # named by `run`, as a declaration of what the base declares
                if not top and names - self.own:
                    self.fail("properties", f"naming {', '.join(sorted(names - self.own))}, which the sub-schema does not declare")
            elif keyword == "required":
                self.own_only(keyword, value)
            elif keyword == "dependentRequired":
                self.own_only(keyword, [*value, *(name for names in value.values() for name in names)])
            elif keyword == "dependentSchemas":
                self.own_only(keyword, list(value))
                for branch in value.values():
                    self.node(branch)
            elif keyword == "patternProperties":
                for pattern in value:
                    hit = sorted(name for name in self.declared if re.search(pattern, name))
                    if hit:
                        self.fail(f"patternProperties {pattern!r}", f"which matches {', '.join(hit)}, declared by {self.base_name}")
            elif keyword in _OPEN:
                if value is not True:
                    self.fail(keyword, f"which constrains {self.base_name} as a whole")
            elif keyword in _APPLICATORS_LIST:
                if not value:
                    self.fail(f"an empty {keyword}", f"which no instance of {self.base_name} matches or constrains it")
                for branch in value:
                    self.node(branch)
            elif keyword in _APPLICATORS_SCHEMA:
                self.node(value)
            else:
                self.fail(keyword, f"which {self.base_name} cannot take from an extension")

    def own_only(self, keyword: str, names) -> None:
        stray = sorted(set(names) - self.own)
        if stray:
            self.fail(keyword, f"naming {', '.join(stray)}, which the sub-schema does not declare, so it constrains {self.base_name}")


def check_additive(extension: RppExtension) -> None:
    for base_name, ext_name in extension.extends.items():
        _Check(extension, ext_name, base_name).run(extension.defs[ext_name])
