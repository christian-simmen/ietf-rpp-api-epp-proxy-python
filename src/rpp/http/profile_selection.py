from dataclasses import dataclass

from rpp.schema.rpp_profile import RppProfile


@dataclass(frozen=True)
class ProfileSelection:
    """The profiles of one request. `request` is the profile the request is read under: its parsing, checking, routing
    and the backend command. `response` is the one the response is under: what it shows and its media type. Core §14.3
    keeps them apart (the `Content-Type` and the `Accept`); the header method of §14.2 has one profile for both.
    """
    request: RppProfile
    response: RppProfile

    @classmethod
    def of(cls, profile: RppProfile) -> "ProfileSelection":
        return cls(request=profile, response=profile)
