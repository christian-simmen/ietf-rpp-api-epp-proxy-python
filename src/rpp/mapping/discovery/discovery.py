from core.model.shared.discovery import Discovery
from rpp.dto.rpp_discovery import RPPDiscovery
from rpp.dto.rpp_discovery_environment import RPPDiscoveryEnvironment
from rpp.dto.rpp_discovery_version import RPPDiscoveryVersion
from rpp.mapping.shared.extension import extension_to_rpp
from rpp.schema.extensions import EXTENSIONS, SERVER_EXTENSIONS
from rpp.schema.https_url import https_url, text
from rpp.schema.validator import validate_schema


def model_to_rpp(discovery: Discovery) -> dict:
    rpp = RPPDiscovery(
        versions=[RPPDiscoveryVersion(version=discovery.version, base_url=discovery.base_url)],
        environment=RPPDiscoveryEnvironment(name=discovery.environment_name, status=discovery.environment_status),
        tlds=discovery.tlds,
        extensions=[extension_to_rpp(EXTENSIONS[extension]) for extension in discovery.extensions] or None,
        profiles=discovery.profiles,
        objects=discovery.objects,
        datetime=discovery.datetime,
    ).to_rpp()
    extensions = ()
    if discovery.profile_schemas is not None:
        # a member of the extension `profile-schemas`, which the server has whatever profile a request has
        rpp["profileSchemas"] = [
            {"profile": reference.profile, "version": reference.version, "url": reference.url}
            for reference in discovery.profile_schemas]
        extensions = SERVER_EXTENSIONS
    validate_schema("discovery.read", rpp, extensions)
    return rpp


def _tld(value) -> bool:
    return text(value) and not any(c.isspace() for c in value)


def invalid_settings(settings) -> list[str]:
    """The names of the settings of the discovery document that are absent or of the wrong shape, never their values.

    `rpp_base_url` must be an absolute https URL (core §22), `rpp_tlds` a non-empty list of strings without whitespace and the
    environment values non-empty strings, none of them padded or with control characters.
    """
    tlds = getattr(settings, "rpp_tlds", None)
    checks = {
        "rpp_base_url": https_url(getattr(settings, "rpp_base_url", None)),
        "rpp_tlds": isinstance(tlds, list) and bool(tlds) and all(_tld(tld) for tld in tlds),
        "rpp_environment_name": text(getattr(settings, "rpp_environment_name", None)),
        "rpp_environment_status": text(getattr(settings, "rpp_environment_status", None)),
    }
    return [key for key, valid in checks.items() if not valid]
