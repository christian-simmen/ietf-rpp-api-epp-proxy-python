from extensions.planets.core.model.satellite_replacement import SatelliteReplacement
from extensions.planets.rpp.dto.rpp_satellite_update import RPPSatelliteUpdate
from rpp.mapping.shared.common import parse_rpp
from rpp.schema.validator import validate_request_schema


def rpp_to_model(satellite_id: str, rpp: dict, extensions: tuple[str, ...] = ()) -> SatelliteReplacement:
    """Converts a full update. A member outside `satellite.update` is rejected, also a create-only or read-only one."""
    validate_request_schema("satellite.update", rpp, extensions)
    return SatelliteReplacement(id=satellite_id, orbitalPeriod=parse_rpp(RPPSatelliteUpdate, rpp).orbitalPeriod)
