from rpp.dto.rpp_profile import RPPProfile
from rpp.mapping.shared.extension import extension_to_rpp
from rpp.mapping.shared.preset_references import profile_references
from rpp.schema.extensions import EXTENSIONS
from rpp.schema.preset_flattening import PresetFlattening
from rpp.schema.rpp_profile import RppProfile
from rpp.schema.validator import validate_schema


def model_to_rpp(profile: RppProfile, flattening: PresetFlattening) -> dict:
    """The Profile Data Object (json §Profile Data Object) of a profile: the same on every server. It is flattened: its
    required extensions include those of its base profiles."""
    rpp = RPPProfile(
        id=profile.id, name=profile.name, description=profile.description, version=profile.version,
        rpp_version=profile.rpp_version, url=profile.url,
        base_profiles=profile_references(profile.base_profiles) or None,
        required_extensions=[extension_to_rpp(EXTENSIONS[ref.id]) for ref in flattening.required_extensions(profile)],
    ).to_rpp()
    validate_schema("profile.read", rpp)
    return rpp
