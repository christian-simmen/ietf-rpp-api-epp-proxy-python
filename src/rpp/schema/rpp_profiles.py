from rpp.schema.extensions import EXTENSIONS
from rpp.schema.profiles import PROFILES
from rpp.schema.rpp_profile import RppProfile


class RppProfiles:
    """The profiles one server offers, in the order of its configuration, and the one it applies by default.

    `build` checks the choice (json §6.11), so a wrong one stops the app: every key is known, the default is one of
    them, names are unique, a profile lists no extension twice and only extensions the proxy implements and the backend
    holds, a base profile is offered and has no base profile itself, and no profile is its own base. The objects of a
    profile need not be held by the backend: a request may use those it holds, see `BackendProfile`.
    """

    def __init__(self, offered: tuple[RppProfile, ...], default: RppProfile):
        self.offered = offered
        self.default = default

    @classmethod
    def build(cls, keys, default_key: str, held_extensions) -> "RppProfiles":
        unknown = sorted(set(keys) - set(PROFILES))
        if unknown:
            raise ValueError(f"backend profile: unknown RPP profile {', '.join(unknown)}")
        if len(set(keys)) != len(keys):
            raise ValueError("backend profile: an RPP profile is offered twice")
        if default_key not in keys:
            raise ValueError(f"backend profile: default_profile {default_key!r} is not one of the offered profiles")
        offered = tuple(PROFILES[key] for key in keys)
        names = [profile.name for profile in offered]
        for profile in offered:
            cls._check(profile, names, held_extensions)
        return cls(offered, PROFILES[default_key])

    @staticmethod
    def _check(profile: RppProfile, names, held_extensions):
        label = f"RPP profile {profile.name}"
        if len(set(profile.extensions)) != len(profile.extensions):
            raise ValueError(f"{label} lists an extension twice")
        missing = sorted(set(profile.extensions) - set(EXTENSIONS))
        if missing:
            raise ValueError(f"{label} lists an extension the proxy does not implement: {', '.join(missing)}")
        unheld = sorted(set(profile.extensions) - set(held_extensions))
        if unheld:
            raise ValueError(f"{label} lists an extension the backend does not hold: {', '.join(unheld)}")
        if profile.base_profile is None:
            return
        if profile.base_profile == profile.name:
            raise ValueError(f"{label} is its own base profile")
        if profile.base_profile not in names:
            raise ValueError(f"{label} has a base profile that is not offered: {profile.base_profile}")
        base = next(other for other in PROFILES.values() if other.name == profile.base_profile)
        if base.base_profile is not None:
            raise ValueError(f"{label} has a base profile that has one itself: {base.name}")

    def by_name(self, name: str) -> RppProfile | None:
        return next((profile for profile in self.offered if profile.name == name), None)

    def extensions(self) -> tuple[str, ...]:
        """The extensions of the offered profiles, each once, in order."""
        return tuple(dict.fromkeys(ext for profile in self.offered for ext in profile.extensions))
