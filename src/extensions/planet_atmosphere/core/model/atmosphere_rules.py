"""The invariants of an atmosphere that the backend checks on what it stores, whatever the way the change came. They repeat the
bounds of the extension schema (docs/demo/planet-atmosphere-extension.md), which `rpp` checks first."""
from extensions.planet_atmosphere.core.model.atmosphere import Atmosphere


def atmosphere_violations(atmosphere: Atmosphere) -> list[str]:
    found = []
    if not atmosphere.pressure >= 0:
        found.append("The pressure of an atmosphere is not negative")
    if atmosphere.dominantGas is not None and not atmosphere.dominantGas:
        found.append("The dominant gas of an atmosphere is not empty")
    return found
