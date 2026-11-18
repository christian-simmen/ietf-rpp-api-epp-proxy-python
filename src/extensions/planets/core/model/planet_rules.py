"""The invariants of a planet and a satellite that the backend checks on the result of a change, whatever the way the
change came. They repeat the bounds of the extension schema (docs/demo/planets-extension.md), which `rpp` checks first."""
from extensions.planets.core.model.planet import PLANET_TYPES


def planet_violations(type: str, radius, mass, password) -> list[str]:
    found = []
    if type not in PLANET_TYPES:
        found.append(f"The type of a planet is one of {', '.join(PLANET_TYPES)}")
    for name, value in (("radius", radius), ("mass", mass)):
        if value is not None and not value > 0:
            found.append(f"The {name} of a planet is greater than 0")
    if not password:
        found.append("A planet has its authInfo")
    return found


def satellite_violations(orbital_period) -> list[str]:
    if orbital_period is not None and not orbital_period > 0:
        return ["The orbital period of a satellite is greater than 0"]
    return []
