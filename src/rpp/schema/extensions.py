"""The RPP extensions the proxy implements, one schema file each (copied from `.spec/` by copy_models.sh) in
`schemas/extensions/`, and those a deployment registers by its configuration (`rpp_extensions`, `register_extension`).
Which of them a deployment offers is the `extensions` of its backend profile."""
import json
from pathlib import Path

from rpp.schema.rpp_extension import RppExtension

FOLDER = Path(__file__).parent / "schemas" / "extensions"

_DEF = "#/$defs/"


def _name(ref: str) -> str:
    if not ref.startswith(_DEF):
        raise ValueError(f"An extension maps definitions of the bundle, not {ref!r}")
    return ref[len(_DEF):]


def _from_schema(schema: dict) -> RppExtension:
    about = schema["rpp:extension"]
    return RppExtension(
        id=about["id"], name=about["name"], version=about["version"], url=schema["$id"],
        extends={_name(base): _name(ext) for base, ext in schema["rpp:extends"].items()},
        defs=schema["$defs"],
        objects=tuple(about.get("objects", ())),
    )


# The extensions that belong to the server and to no profile: discovery lists them next to those of the profiles.
SERVER_EXTENSIONS = ("urn:ietf:params:rpp:extension:profile-schemas",)

def _load(path: Path) -> RppExtension:
    with open(path, encoding="utf-8") as f:
        return _from_schema(json.load(f))


EXTENSIONS: dict[str, RppExtension] = {
    extension.id: extension for extension in map(_load, sorted(FOLDER.glob("*.json")))
}


def register_extension(schema: dict) -> RppExtension:
    """Adds the extension of a schema a configured extension registered. It is process-global and keyed by id, so
    registering it again is no change. Only `register()` of an extension the configuration names calls this."""
    extension = _from_schema(schema)
    if extension.id not in EXTENSIONS:
        EXTENSIONS[extension.id] = extension
    return EXTENSIONS[extension.id]


def added_members(schema_name: str, extensions) -> frozenset[str]:
    """The members the given extensions add to a base definition."""
    return frozenset(
        member
        for extension in extensions
        if schema_name in EXTENSIONS[extension].extends
        for member in EXTENSIONS[extension].defs[EXTENSIONS[extension].extends[schema_name]].get("properties", {})
    )


def check_known(extensions):
    """A profile that offers an extension the proxy does not implement is refused, so the app does not start."""
    unknown = sorted(set(extensions) - set(EXTENSIONS))
    if unknown:
        raise ValueError(f"backend profile: unknown RPP extension {', '.join(unknown)}")


def own_definitions() -> dict[str, str]:
    """The definitions of the objects and types the extensions define, by the name a mapper validates with
    (`requestContact.create`), to the name of the extension's definition: with a prefix (`ext.rri.requestContact.create`),
    or the same name where an extension of new objects names them as the base definitions are (`planet.create`). The
    definitions an extension composes with a base one are not among them."""
    names = {}
    for extension in EXTENSIONS.values():
        composed = set(extension.extends.values())
        for name in extension.defs:
            if name in composed:
                continue
            names[name.split(".", 2)[2] if name.startswith("ext.") else name] = name
    return names
