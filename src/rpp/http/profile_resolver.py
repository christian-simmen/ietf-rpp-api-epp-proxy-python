from decimal import Decimal

from connexion import ProblemException

from core.result.result_code import ResultCode
from rpp.http import profile_header
from rpp.http.headers import problem_headers
from rpp.schema.rpp_profile import RppProfile
from rpp.schema.rpp_profiles import RppProfiles

HEADER_SIGNALLING = "header"
MEDIA_TYPE_SIGNALLING = "media-type"
SIGNALLING_METHODS = (HEADER_SIGNALLING, MEDIA_TYPE_SIGNALLING)


def _refused(code: ResultCode, detail: str) -> ProblemException:
    return ProblemException(status=400, title=code.value[1], detail=detail, headers=problem_headers(code))


def _values(scope, name: str) -> list[str]:
    key = name.lower().encode("latin-1")
    return [value.decode("latin-1") for header, value in scope["headers"] if header == key]


class ProfileResolver:
    """Selects the profile of a request: the one place that knows how a client names it.

    A request that names none gets the default of the server (core §14). A signalling method (the `RPP-Profile` header,
    or the parameters of the media type) reads the request's `scope` here, and raises a `ProblemException` (400, with
    an RPP client error code) for a value it cannot read or a profile or version the server does not offer; nothing
    else needs to know. Only `header` is implemented (core §14.2): the parameters of the media type (§14.3) mean the
    other method, so they are refused.
    """

    def __init__(self, profiles: RppProfiles, signalling: str = HEADER_SIGNALLING):
        if signalling != HEADER_SIGNALLING:
            raise ValueError(f"rpp_profile_signalling {signalling!r} is not implemented")
        self._profiles = profiles

    def resolve(self, scope) -> RppProfile:
        # Core §14: the two methods MUST NOT be used simultaneously.
        if profile_header.has_profile_parameters(_values(scope, "Accept") + _values(scope, "Content-Type")):
            raise _refused(ResultCode.COMMAND_SYNTAX_ERROR,
                           "This server signals the profile with the RPP-Profile header field: "
                           "the media type takes no profile parameters")
        try:
            named = profile_header.parse(_values(scope, profile_header.HEADER))
        except profile_header.ProfileHeaderError as error:
            raise _refused(error.code, str(error)) from None
        if named is None:
            return self._profiles.default
        name, version = named
        profile = self._profiles.by_name(name)
        if profile is None:
            raise _refused(ResultCode.PARAMETER_VALUE_RANGE_ERROR, f"This server does not offer the profile {name}")
        if Decimal(profile.version) != version:  # compared as decimals: 1.10 is 1.1 (RFC 9651)
            raise _refused(ResultCode.PARAMETER_VALUE_RANGE_ERROR,
                           f"This server does not offer version {version} of the profile {name}")
        return profile
