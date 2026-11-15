from rpp.dto.rpp_profile import RPPProfile
from rpp.dto.rpp_profile_reference import RPPProfileReference
from rpp.mapping.shared.extension import extension_to_rpp
from rpp.schema.extensions import EXTENSIONS
from rpp.schema.rpp_profile import RppProfile
from rpp.schema.validator import validate_schema


def model_to_rpp(profile: RppProfile, default: bool) -> dict:
    """The Profile Data Object (json §6.11.1) of a profile definition: the same on every server, whatever the backend
    holds, but for `defaultProfile`."""
    rpp = RPPProfile(
        name=profile.name, description=profile.description, version=profile.version, rpp_version=profile.rpp_version,
        objects=list(profile.objects),
        extensions=[extension_to_rpp(EXTENSIONS[extension]) for extension in profile.extensions] or None,
        base_profile=RPPProfileReference(name=profile.base_profile) if profile.base_profile else None,
        default_profile=default,
    ).to_rpp()
    validate_schema("profile.read", rpp)
    return rpp
