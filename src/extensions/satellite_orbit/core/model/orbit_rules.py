"""The invariants of an orbit that the backend checks on what it stores, whatever the way the change came. They repeat the bounds
of the extension schema (docs/demo/satellite-orbit-extension.md), which `rpp` checks first."""
from extensions.satellite_orbit.core.model.orbit import Orbit


def orbit_violations(orbit: Orbit) -> list[str]:
    found = []
    if not orbit.semiMajorAxis > 0:
        found.append("The semi-major axis of an orbit is greater than 0")
    if orbit.eccentricity is not None and not 0 <= orbit.eccentricity < 1:
        found.append("The eccentricity of an orbit is at least 0 and below 1")
    if orbit.inclination is not None and not 0 <= orbit.inclination <= 180:
        found.append("The inclination of an orbit is between 0 and 180 degrees")
    return found
