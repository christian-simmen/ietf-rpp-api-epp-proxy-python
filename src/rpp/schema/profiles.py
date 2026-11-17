"""The RPP profiles the proxy knows, one definition file each in `schemas/profiles/`. Which of them a server offers, and
its default, are `profiles` and `default_profile` of its backend profile; `RppProfiles` is that choice, checked."""
from pathlib import Path

import yaml

from rpp.schema.rpp_profile import RppProfile

FOLDER = Path(__file__).parent / "schemas" / "profiles"


def _profile(key: str, data: dict) -> RppProfile:
    return RppProfile(
        key=key, name=data["name"], description=data["description"], version=data["version"],
        rpp_version=data["rppVersion"], objects=tuple(data["objects"]), extensions=tuple(data.get("extensions") or ()),
        base_profile=data.get("baseProfile"),
    )


def _load(path: Path) -> RppProfile:
    with open(path, encoding="utf-8") as f:
        return _profile(path.stem, yaml.safe_load(f))


PROFILES: dict[str, RppProfile] = {profile.key: profile for profile in map(_load, sorted(FOLDER.glob("*.yaml")))}


def register_profile(key: str, data: dict) -> RppProfile:
    """Adds the RPP profile a configured extension brings, as its definition file would state it. Process-global and
    keyed by `key`: a profile registered already stays as it is."""
    if key not in PROFILES:
        PROFILES[key] = _profile(key, data)
    return PROFILES[key]
