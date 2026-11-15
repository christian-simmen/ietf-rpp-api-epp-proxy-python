from decimal import Decimal

from connexion import ProblemException

from core.result.result_code import ResultCode
from rpp.http import profile_header
from rpp.http.headers import problem_headers
from rpp.http.profile_selection import ProfileSelection
from rpp.http.asgi_headers import request_values, rewriting_start, values_of, without
from rpp.schema.rpp_profile import RppProfile
from rpp.schema.rpp_profiles import RppProfiles


def _refused(code: ResultCode, detail: str) -> ProblemException:
    return ProblemException(status=400, title=code.value[1], detail=detail, headers=problem_headers(code))


class HeaderProfileSignalling:
    """Selects the profile of a request with the `RPP-Profile` header field (core §14.2), and shows the applied one in
    the response (core §6.2).

    A request that names none gets the default of the server (core §14). It raises a `ProblemException` (400, with an RPP
    client error code) for a value it cannot read or a profile or version the server does not offer. The parameters of
    the media type (§14.3) mean the other method, so they are refused. The request and the response have one profile.
    """

    def __init__(self, profiles: RppProfiles):
        self._profiles = profiles

    def resolve(self, scope) -> ProfileSelection:
        return ProfileSelection.of(self._resolve(scope))

    def _resolve(self, scope) -> RppProfile:
        # Core §14: the two methods MUST NOT be used simultaneously.
        if profile_header.has_profile_parameters(request_values(scope, "Accept") + request_values(scope, "Content-Type")):
            raise _refused(ResultCode.COMMAND_SYNTAX_ERROR,
                           "This server signals the profile with the RPP-Profile header field: "
                           "the media type takes no profile parameters")
        try:
            named = profile_header.parse(request_values(scope, profile_header.HEADER))
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

    def announce(self, send, selection: ProfileSelection):
        """`send` that adds the `RPP-Profile` header of the applied profile to the response (core §6.2)."""
        profile = selection.response

        def rewrite(status, headers):
            vary = ", ".join(values_of(headers, "Vary"))
            return [*without(headers, "Vary"), (profile_header.HEADER.lower().encode(),
                                                profile_header.format_profile(profile).encode()),
                    (b"vary", profile_header.vary_with_profile(vary).encode("latin-1"))]
        return rewriting_start(send, rewrite)

    def problem_headers(self, selection: ProfileSelection, headers: dict) -> dict:
        """The headers of a Problem Detail rendered after the selection."""
        return {**headers, profile_header.HEADER: profile_header.format_profile(selection.response),
                "Vary": profile_header.vary_with_profile(headers.get("Vary"))}
