import copy
from urllib.parse import quote

from rpp.schema.extensions import EXTENSIONS
from rpp.schema.rpp_profile import RppProfile
from rpp.schema.rpp_profiles import RppProfiles
from rpp.schema.validator import build_effective, bundle_definitions

JSON_SCHEMA = "https://json-schema.org/draft/2020-12/schema"
MEDIA_TYPE = "application/schema+json"


def schema_path(name: str) -> str:
    """The path of the effective schema of a profile; the name is one path segment."""
    return f"/profiles/{quote(name, safe='')}/schema"


def schema_url(base_url: str, name: str) -> str:
    """The public URL of the effective schema of a profile."""
    return base_url.rstrip("/") + schema_path(name)


class ProfileSchemas:
    """The effective schema of each offered profile (json §7.2), built once when the app is built and then only read.

    Building also fills the validators of the profile's extensions (`build_effective`), so a request never composes a
    schema. The document of a profile is a JSON Schema 2020-12 whose `$defs` hold the bundle and the definitions of the
    profile's extensions. A definition an extension extends is the `allOf` of the base definition and the extension's
    ones, as validation composes it, so what is published is what is enforced. (The drafts reach such a definition only
    from an operation, not from another definition, so composing it in place changes no other.)
    """

    def __init__(self, profiles: RppProfiles, base_url: str | None):
        self._documents = {}
        for profile in profiles.offered:
            build_effective(profile.extensions)
            self._documents[profile.key] = self._document(profile, base_url)

    @staticmethod
    def _document(profile: RppProfile, base_url: str | None) -> dict:
        definitions = copy.deepcopy(bundle_definitions())
        added = {}
        for extension in profile.extensions:
            definitions.update(copy.deepcopy(EXTENSIONS[extension].defs))
            for base, ext in EXTENSIONS[extension].extends.items():
                added.setdefault(base, []).append({"$ref": f"#/$defs/{ext}"})
        for base, parts in added.items():
            definitions[base] = {"allOf": [definitions[base], *parts]}
        document = {"$schema": JSON_SCHEMA}
        if base_url:
            document["$id"] = schema_url(base_url, profile.name)
        document["title"] = f"Effective schema of the RPP profile {profile.name} version {profile.version}"
        document["$defs"] = definitions
        return document

    def of(self, profile: RppProfile) -> dict:
        return self._documents[profile.key]
