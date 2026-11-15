from connexion import ProblemException

from core.result.result_code import ResultCode
from rpp.http.extension_paths import plural
from rpp.http.headers import problem_headers
from rpp.http.profile_header import HEADER, format_profile, vary_with_profile
from rpp.http.profile_resolver import ProfileResolver
from rpp.http.request_profiles import RequestProfiles
from rpp.schema.extensions import EXTENSIONS
from rpp.schema.rpp_profile import RppProfile

# The key of the request context that holds the selected `RppProfile`.
SELECTED_PROFILE = "rpp_profile"

# The first path segment of the data objects of the drafts, and the object it addresses.
COLLECTIONS = {plural(obj): obj for obj in ("domainName", "contact", "host")}


def with_profile_header(send, profile: RppProfile):
    """`send` that adds the `RPP-Profile` header of the applied profile to the response (core §6.2)."""
    async def send_with_profile(message):
        if message["type"] == "http.response.start":
            headers = [(name, value) for name, value in message.get("headers", []) if name.lower() != b"vary"]
            vary = b", ".join(value for name, value in message.get("headers", []) if name.lower() == b"vary")
            message = {**message, "headers": [
                *headers, (HEADER.lower().encode(), format_profile(profile).encode()),
                (b"vary", vary_with_profile(vary.decode("latin-1")).encode("latin-1"))]}
        await send(message)
    return send_with_profile


class ProfileMiddleware:
    """Selects the profile of each request and refuses what it does not allow, before anything else of the application.

    The selected profile is put in the request context. A path of a data object that the profile does not have, or the
    backend does not hold, is a 501 `02307`: core §16.1.6 lets a server answer an endpoint it does not implement with
    404 or 501, and result code 02307 is the unimplemented object service. A path no operation serves is the router's
    404, with no profile selected. The response names the applied profile in `RPP-Profile` (core §6.2); the Problem
    Details that an outer error handler renders get it from `handle_rpp_error`. Paths of no object (`/messages`, discovery,
    profiles) are always allowed. It runs after the authentication, so a request that is not authenticated is still a
    401 and gives no hint of the profiles.
    """

    def __init__(self, app, resolver: ProfileResolver, request_profiles: RequestProfiles, extensions):
        self.app = app
        # The objects an extension defines are in the plural of their identifier (core §16.1). Only those of the
        # offered extensions have paths: any other is a 404, as without the extension.
        self.collections = {**COLLECTIONS, **{
            plural(obj): obj for extension in extensions for obj in EXTENSIONS[extension].objects}}
        self.resolver = resolver
        self.request_profiles = request_profiles

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Only a routed operation selects a profile and is refused: a path no operation serves stays the 404 of
            # the router, and a 401 never gets here.
            routed = scope.get("extensions", {}).get("connexion_routing", {}).get("operation_id")
            if not routed:
                await self.app(scope, receive, send)
                return
            profile = self.resolver.resolve(scope)
            scope.setdefault("extensions", {}).setdefault("connexion_context", {})[SELECTED_PROFILE] = profile
            send = with_profile_header(send, profile)
            segment = scope["path"].lstrip("/").split("/", 1)[0]
            obj = self.collections.get(segment)
            if obj is not None and obj not in self.request_profiles.of(profile).objects:
                raise ProblemException(
                    status=501, title=ResultCode.UNIMPLEMENTED_OBJECT_SERVICE.value[1],
                    detail=f"The profile {profile.name} has no {obj} object on this server",
                    headers=problem_headers(ResultCode.UNIMPLEMENTED_OBJECT_SERVICE),
                )
        await self.app(scope, receive, send)
