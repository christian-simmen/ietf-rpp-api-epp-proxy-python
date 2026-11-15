from rpp.schema.rpp_profile import RppProfile
from rpp.schema.rpp_profiles import RppProfiles


class ProfileResolver:
    """Selects the profile of a request: the one place that knows how a client names it.

    A request that names none gets the default of the server (core §14). A signalling method (the `RPP-Profile` header,
    or the parameters of the media type) reads the request's `scope` here, and raises a `ProblemException` for a
    profile or version the server does not offer; nothing else needs to know.
    """

    def __init__(self, profiles: RppProfiles):
        self._profiles = profiles

    def resolve(self, scope) -> RppProfile:
        return self._profiles.default
