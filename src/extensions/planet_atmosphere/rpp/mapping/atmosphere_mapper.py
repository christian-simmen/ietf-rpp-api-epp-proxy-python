"""The JSON of the member `atmosphere` and the typed object of the core of this extension, for the mappers of a planet."""
from extensions.planet_atmosphere.core.model.atmosphere import Atmosphere
from extensions.planet_atmosphere.core.model.atmosphere_changes import AtmosphereChanges
from extensions.planet_atmosphere.core.model.extension_id import EXTENSION_ID
from extensions.planet_atmosphere.rpp.dto.rpp_atmosphere import RPPAtmosphere
from rpp.mapping.shared.common import parse_rpp

MEMBER = "atmosphere"


def _atmosphere(rpp: dict) -> Atmosphere:
    dto = parse_rpp(RPPAtmosphere, rpp)
    return Atmosphere(pressure=dto.pressure, dominantGas=dto.dominantGas)


class AtmosphereMapper:
    """The member mapper of the planets extension (`MemberMapper`) for the atmosphere of a planet."""
    extension_id = EXTENSION_ID
    members = (MEMBER,)

    def to_model(self, members: dict) -> Atmosphere:
        return _atmosphere(members[MEMBER])

    def to_changes(self, values: dict, cleared: frozenset[str]) -> AtmosphereChanges:
        if MEMBER in values:
            return AtmosphereChanges(atmosphere=_atmosphere(values[MEMBER]))
        return AtmosphereChanges(removed=True)

    def to_rpp(self, value: Atmosphere) -> dict:
        return {MEMBER: RPPAtmosphere(pressure=value.pressure, dominantGas=value.dominantGas).to_rpp()}
