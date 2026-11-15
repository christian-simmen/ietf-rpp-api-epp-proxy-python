from core.capabilities.backend_profile import BackendProfile
from rpp.schema.rpp_profile import RppProfile
from rpp.schema.rpp_profiles import RppProfiles


class RequestProfiles:
    """The backend profile as a request under each offered profile sees it, made once when the app is built.

    The extensions are those of the selected profile, so the combined schema (guidelines §8.6) holds only them. The
    objects are those the profile has and the backend holds: a profile may list an object the backend lacks, the
    request cannot use it.
    """

    def __init__(self, backend: BackendProfile, profiles: RppProfiles):
        self._by_key = {
            profile.key: backend.with_changes({
                "extensions": list(profile.extensions),
                "objects": [obj for obj in backend.objects if obj in profile.objects],
            })
            for profile in profiles.offered
        }

    def of(self, profile: RppProfile) -> BackendProfile:
        return self._by_key[profile.key]
