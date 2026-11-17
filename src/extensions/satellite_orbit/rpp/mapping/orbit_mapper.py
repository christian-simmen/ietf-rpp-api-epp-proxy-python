"""The JSON of the member `orbit` and the typed object of the core of this extension, for the mappers of a satellite."""
from extensions.satellite_orbit.core.model.extension_id import EXTENSION_ID
from extensions.satellite_orbit.core.model.orbit import Orbit
from extensions.satellite_orbit.core.model.orbit_changes import OrbitChanges
from extensions.satellite_orbit.rpp.dto.rpp_orbit import RPPOrbit
from rpp.mapping.shared.common import parse_rpp

MEMBER = "orbit"


def _orbit(rpp: dict) -> Orbit:
    dto = parse_rpp(RPPOrbit, rpp)
    return Orbit(semiMajorAxis=dto.semiMajorAxis, eccentricity=dto.eccentricity, inclination=dto.inclination)


class OrbitMapper:
    """The member mapper of the planets extension (`MemberMapper`) for the orbit of a satellite."""
    extension_id = EXTENSION_ID
    members = (MEMBER,)

    def to_model(self, members: dict) -> Orbit:
        return _orbit(members[MEMBER])

    def to_changes(self, values: dict, cleared: frozenset[str]) -> OrbitChanges:
        if MEMBER in values:
            return OrbitChanges(orbit=_orbit(values[MEMBER]))
        return OrbitChanges(removed=True)

    def to_rpp(self, value: Orbit) -> dict:
        return {MEMBER: RPPOrbit(semiMajorAxis=value.semiMajorAxis, eccentricity=value.eccentricity,
                                 inclination=value.inclination).to_rpp()}
