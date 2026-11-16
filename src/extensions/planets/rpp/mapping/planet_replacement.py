from extensions.planets.core.model.planet_replacement import PlanetReplacement
from extensions.planets.rpp.dto.rpp_planet_update import RPPPlanetUpdate
from rpp.mapping.shared import auth_info
from rpp.mapping.shared.common import parse_rpp
from rpp.schema.validator import validate_schema


def rpp_to_model(planet_id: str, rpp: dict, extensions: tuple[str, ...] = ()) -> PlanetReplacement:
    """Converts a full update. A member outside `planet.update` is rejected, also a create-only or read-only one."""
    validate_schema("planet.update", rpp, extensions)
    update = parse_rpp(RPPPlanetUpdate, rpp)
    return PlanetReplacement(id=planet_id, type=update.type, radius=update.radius, mass=update.mass,
                             authInfo=auth_info.rpp_to_model(update.authInfo))
