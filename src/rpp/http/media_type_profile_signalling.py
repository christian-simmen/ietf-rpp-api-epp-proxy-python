from decimal import Decimal

from connexion import ProblemException

from core.result.result_code import ResultCode
from rpp.http import media_range
from rpp.http.asgi_headers import request_values, rewriting_start, values_of, without
from rpp.http.headers import RPP_MEDIA_TYPE, problem_headers
from rpp.http.media_range import MediaRange
from rpp.http.media_range_error import MediaRangeError
from rpp.http.profile_header import HEADER as PROFILE_HEADER
from rpp.http.profile_selection import ProfileSelection
from rpp.http.vary import vary_with
from rpp.schema.rpp_profile import RppProfile
from rpp.schema.rpp_profiles import RppProfiles

# What a media range of an Accept says about a profile, from the least to the most specific (RFC 9110 §12.5.1).
ANY, ANY_APPLICATION, DEFAULT_ONLY, EXACT = 0, 1, 2, 3


def _refused(status: int, code: ResultCode, detail: str) -> ProblemException:
    return ProblemException(
        status=status, title=code.value[1], detail=detail,
        headers={**problem_headers(code), "Vary": "Accept"})


class MediaTypeProfileSignalling:
    """Selects the profile of a request with the media type parameters `profile` and `profile-version` (core §14.3),
    and shows the applied one in the `Content-Type` of the response.

    The request profile is that of the request's `Content-Type`, for every request with content or without (§13 asks
    for one on every request; a missing one, or one without the parameters, is the default profile). The response
    profile is chosen from `Accept` by weight (core §13, RFC 9110 §12.5.1). A range with the profile parameters stands for that profile. An `application/rpp+json`
    range without them stands for the default profile, as a request without parameters gets it (§14.3), and
    `application/*` and `*/*` for every profile offered. The most specific range that matches a profile gives its weight;
    a weight of 0 excludes it. Of the profiles of the highest weight the request profile is answered if it is among
    them, else that of the first range of the Accept (the default, if a wildcard is that range). Without an `Accept` the default profile is acceptable.

    The refusals are 415 for a profile or version of the `Content-Type` that the server does not offer, 406 when none of
    the `Accept` is, and 400 when the request profile is not listed in the `Accept`, when a value cannot be read, and for
    the `RPP-Profile` header (both methods in use, §14). Each has an RPP result code and `Vary: Accept`. The response
    carries no `RPP-Profile` header, which would be the second method (§14).
    """

    def __init__(self, profiles: RppProfiles):
        self._profiles = profiles

    def resolve(self, scope) -> ProfileSelection:
        # Core §14: the two methods MUST NOT be used simultaneously.
        if request_values(scope, PROFILE_HEADER):
            raise _refused(400, ResultCode.COMMAND_SYNTAX_ERROR,
                           "This server signals the profile with the media type parameters profile and "
                           f"profile-version: the {PROFILE_HEADER} header field is not used")
        try:
            ranges = media_range.parse_accept(request_values(scope, "Accept"))
            request = self._request_profile(scope)
            weights = self._acceptable(ranges)
        except MediaRangeError as error:
            raise _refused(400, error.code, str(error)) from None
        if not weights:
            raise _refused(406, ResultCode.PARAMETER_VALUE_RANGE_ERROR,
                           "The Accept field lists no profile this server offers")
        if request.key not in weights:
            raise _refused(400, ResultCode.COMMAND_SYNTAX_ERROR,
                           f"The profile of the request, {request.name}, is not listed in the Accept field")
        best = max(quality for quality, _ in weights.values())
        tied = {key: position for key, (quality, position) in weights.items() if quality == best}
        if request.key in tied:
            chosen = request.key
        else:
            # one range (a wildcard) can stand for several: the default of the server is the one it means
            chosen = min(tied, key=lambda key: (tied[key], key != self._profiles.default.key))
        return ProfileSelection(request=request, response=next(
            profile for profile in self._profiles.offered if profile.key == chosen))

    def _offered(self, name: str, version: Decimal) -> RppProfile | None:
        profile = self._profiles.by_name(name)
        # compared as decimals, as the header method does: 1.10 is 1.1
        return profile if profile is not None and Decimal(profile.version) == version else None

    def _request_profile(self, scope) -> RppProfile:
        values = request_values(scope, "Content-Type")
        if len(values) > 1:
            raise MediaRangeError(ResultCode.PARAMETER_VALUE_SYNTAX_ERROR, "The request has several Content-Type fields")
        content_type = media_range.parse_media_type(values[0]) if values else None
        named = content_type.profile() if content_type is not None and content_type.kind == RPP_MEDIA_TYPE else None
        if named is None:
            return self._profiles.default  # no parameters: the default profile (§14.3)
        profile = self._offered(*named)
        if profile is None:
            raise _refused(415, ResultCode.PARAMETER_VALUE_RANGE_ERROR,
                           f"This server does not offer version {named[1]} of the profile {named[0]} for requests")
        return profile

    def _acceptable(self, ranges: list[MediaRange]) -> dict[str, tuple[Decimal, int]]:
        """The offered profiles of weight above 0, by key, with their weight and the position of the range that gave
        it."""
        if not ranges:
            return {self._profiles.default.key: (Decimal(1), 0)}
        found: dict[str, tuple[int, Decimal, int]] = {}  # key -> (specificity, weight, position)
        for position, item in enumerate(ranges):
            for specificity, profile in self._matches(item):
                best = found.get(profile.key)
                if best is None or (specificity, item.quality) > best[:2]:
                    found[profile.key] = (specificity, item.quality, position)
        return {key: (weight, position) for key, (_, weight, position) in found.items() if weight > 0}

    def _matches(self, item: MediaRange):
        """The profiles a range stands for, with how specific the range is."""
        if item.kind == "*/*":
            return [(ANY, profile) for profile in self._profiles.offered]
        if item.kind == "application/*":
            return [(ANY_APPLICATION, profile) for profile in self._profiles.offered]
        if item.kind != RPP_MEDIA_TYPE:
            return []
        named = item.profile()
        if named is None:
            return [(DEFAULT_ONLY, self._profiles.default)]
        profile = self._offered(*named)
        return [(EXACT, profile)] if profile is not None else []

    def announce(self, send, selection: ProfileSelection):
        """`send` that gives a successful RPP response the profile applied in its `Content-Type` (§14.3), and lists
        `Accept` in `Vary`."""
        profile = selection.response
        applied = f'{RPP_MEDIA_TYPE}; profile="{profile.name}"; profile-version="{profile.version}"'

        def rewrite(status, headers):
            vary = ", ".join(values_of(headers, "Vary"))
            headers = [*without(headers, "Vary"), (b"vary", vary_with(vary, "Accept").encode("latin-1"))]
            if 200 <= status < 300 and [value.lower() for value in values_of(headers, "Content-Type")] == [RPP_MEDIA_TYPE]:
                headers = [*without(headers, "Content-Type"), (b"content-type", applied.encode("latin-1"))]
            return headers
        return rewriting_start(send, rewrite)

    def problem_headers(self, selection: ProfileSelection, headers: dict) -> dict:
        """The headers of a Problem Detail rendered after the selection: no profile parameters, no `RPP-Profile`."""
        return {**headers, "Vary": vary_with(headers.get("Vary"), "Accept")}
