from core.model.shared.availability import Availability
from extensions.planets.rpp.dto.rpp_planet_availability import RPPPlanetAvailability
from rpp.schema.validator import validate_schema


def model_to_rpp(check: Availability, extensions: tuple[str, ...] = ()) -> dict:
    availability = RPPPlanetAvailability(
        available=check.available, reason=None if check.available else check.reason).to_rpp()
    validate_schema("planetAvailability.read", availability, extensions)
    return availability
