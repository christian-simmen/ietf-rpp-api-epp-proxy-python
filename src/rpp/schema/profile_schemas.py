from urllib.parse import quote

from rpp.schema.effective_schema import effective_definitions
from rpp.schema.extensions import SERVER_EXTENSIONS
from rpp.schema.rpp_profile import RppProfile
from rpp.schema.rpp_profiles import RppProfiles
from rpp.schema.validator import build_effective

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

    The document of a profile is a JSON Schema 2020-12 whose `$defs` are the combined schema of extension guidelines
    §8.6 for the profile's extensions (`effective_schema.py`): the bundle and the extensions' definitions, each extended
    definition the `allOf` of the base definition and the extension's, and `"unevaluatedProperties": false` injected at
    every object-schema node (json §4.9.1). Building also fills the validators of the profile (`build_effective`) on those
    very `$defs`, so a request never composes a schema, and what is published is what is enforced.
    """

    def __init__(self, profiles: RppProfiles, base_url: str | None):
        self._documents = {}
        build_effective(SERVER_EXTENSIONS)      # what the discovery document is validated with
        for profile in profiles.offered:
            build_effective(profile.extensions)     # what a request of the profile is validated with
            build_effective((*profile.extensions, *SERVER_EXTENSIONS))     # what the document publishes
            self._documents[profile.key] = self._document(profile, base_url)

    @staticmethod
    def _document(profile: RppProfile, base_url: str | None) -> dict:
        document = {"$schema": JSON_SCHEMA}
        if base_url:
            document["$id"] = schema_url(base_url, profile.name)
        document["title"] = f"Effective schema of the RPP profile {profile.name} version {profile.version}"
        # the profile's own extensions and the server's: the schema also accepts the server's discovery document
        document["$defs"] = effective_definitions((*profile.extensions, *SERVER_EXTENSIONS))
        return document

    def of(self, profile: RppProfile) -> dict:
        return self._documents[profile.key]
