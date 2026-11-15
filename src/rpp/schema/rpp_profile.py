from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class RppProfile:
    """An RPP profile (json §6.11) as its definition file states it. The definition is the same on every server: it is
    what the Profile Data Object publishes. `key` is the file's name, which a server's configuration names it by.

    `objects` and `extensions` (ids) are complete: a profile with a `base_profile` does not inherit from it, the
    inheritance is informational and checked at start. `base_profile` is the name of the base profile.
    """
    key: str
    name: str
    description: str
    version: str
    rpp_version: str
    objects: tuple[str, ...]
    extensions: tuple[str, ...] = ()
    base_profile: str | None = None
