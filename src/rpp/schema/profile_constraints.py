"""What a Profile Schema maps (json §Profile Schema): `rpp:constraints` names the definitions it constrains by absolute URI
and the sub-schemas that constrain them by JSON Pointer. The URI is that of the base schema (`BASE_SCHEMA`) or of the schema of
an extension the profile requires (its `$id`)."""
from dataclasses import dataclass

from rpp.schema.bundle_definitions import bundle_definitions
from rpp.schema.extensions import EXTENSIONS
from rpp.schema.rpp_profile import RppProfile

BASE_SCHEMA = "urn:ietf:params:rpp:schema:json-1.0"
_DEFS = "#/$defs/"


def _name(pointer: str, where: str) -> str:
    if not pointer.startswith(_DEFS) or "/" in pointer[len(_DEFS):]:
        raise ValueError(f"{where}: {pointer!r} is not a pointer to a definition of the Profile Schema")
    return pointer[len(_DEFS):]


@dataclass(frozen=True)
class ProfileConstraints:
    """The constraints of one profile: for each constrained definition, `(extension id or None, sub-schema keys)`."""
    profile: RppProfile
    targets: dict[str, tuple[str | None, tuple[str, ...]]]

    @classmethod
    def of(cls, profile: RppProfile, required_extensions) -> "ProfileConstraints":
        schema = profile.schema
        if schema is None:
            return cls(profile, {})
        label = f"The Profile Schema of {profile.id}"
        about = schema.get("rpp:profile") or {}
        if about.get("id") != profile.id or str(about.get("version")) != profile.version:
            raise ValueError(f"{label} states rpp:profile {about}, not {profile.id} {profile.version}")
        if "rpp:extends" in schema:
            raise ValueError(f"{label} contains rpp:extends")
        if "$id" not in schema:
            raise ValueError(f"{label} has no $id")
        by_schema = {EXTENSIONS[ext].url: ext for ext in required_extensions if ext in EXTENSIONS}
        targets: dict[str, tuple[str | None, list[str]]] = {}
        for uri, pointer in (schema.get("rpp:constraints") or {}).items():
            schema_uri, _, fragment = uri.partition("#")
            definition = _name("#" + fragment, label)
            if schema_uri == BASE_SCHEMA:
                extension = None
                if definition not in bundle_definitions():
                    raise ValueError(f"{label} constrains {definition}, which does not exist in RPP")
            elif schema_uri in by_schema:
                extension = by_schema[schema_uri]
                if definition not in EXTENSIONS[extension].defs:
                    raise ValueError(f"{label} constrains {definition}, which the extension {extension} does not define")
            else:
                unrequired = next((ext.id for ext in EXTENSIONS.values() if ext.url == schema_uri), None)
                if unrequired is not None:
                    raise ValueError(f"{label} constrains {definition} of the extension {unrequired}, "
                                     f"which the profile does not require")
                raise ValueError(f"{label} constrains {uri}, a schema of neither RPP nor an extension the profile requires")
            known = targets.setdefault(definition, (extension, []))
            sub = _name(pointer, label)
            if sub not in schema.get("$defs", {}):
                raise ValueError(f"{label} maps {uri} to {pointer}, which it does not define")
            if sub not in known[1]:
                known[1].append(sub)
        return cls(profile, {name: (ext, tuple(subs)) for name, (ext, subs) in targets.items()})
