from core.model.shared.availability import Availability
from extensions.planets.rpp.dto.rpp_satellite_availability import RPPSatelliteAvailability
from rpp.schema.validator import validate_schema


def model_to_rpp(check: Availability, extensions: tuple[str, ...] = ()) -> dict:
    availability = RPPSatelliteAvailability(
        available=check.available, reason=None if check.available else check.reason).to_rpp()
    validate_schema("satelliteAvailability.read", availability, extensions)
    return availability
