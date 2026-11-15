from rpp.http.header_profile_signalling import HeaderProfileSignalling
from rpp.http.media_type_profile_signalling import MediaTypeProfileSignalling
from rpp.schema.rpp_profiles import RppProfiles

HEADER_SIGNALLING = "header"
MEDIA_TYPE_SIGNALLING = "media-type"

_METHODS = {HEADER_SIGNALLING: HeaderProfileSignalling, MEDIA_TYPE_SIGNALLING: MediaTypeProfileSignalling}


def profile_signalling(method: str, profiles: RppProfiles):
    """The signalling method of `rpp_profile_signalling` (core §14): it selects the profile of a request and shows the
    applied one in the response."""
    if method not in _METHODS:
        raise ValueError(f"rpp_profile_signalling must be one of {', '.join(_METHODS)}, not {method!r}")
    return _METHODS[method](profiles)
