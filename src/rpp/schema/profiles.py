"""The RPP profiles the proxy knows, one definition file each in `schemas/profiles/`. Which of them a server offers, and
its default, are `profiles` and `default_profile` of its backend profile; `RppProfiles` is that choice, checked."""
from pathlib import Path

import yaml

from rpp.schema.rpp_profile import RppProfile

FOLDER = Path(__file__).parent / "schemas" / "profiles"


def _load(path: Path) -> RppProfile:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return RppProfile(
        key=path.stem, name=data["name"], description=data["description"], version=data["version"],
        rpp_version=data["rppVersion"], objects=tuple(data["objects"]), extensions=tuple(data.get("extensions") or ()),
        base_profile=data.get("baseProfile"),
    )


PROFILES: dict[str, RppProfile] = {profile.key: profile for profile in map(_load, sorted(FOLDER.glob("*.yaml")))}
