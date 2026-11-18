"""The planet of the planets extension (docs/demo/planets-extension.md)."""
from extensions.planets.core.model.planet import Planet
from extensions.planets.rpp.dto.rpp_planet import RPPPlanet
from extensions.planets.rpp.dto.rpp_satellite_reference import RPPSatelliteReference
from extensions.planets.rpp.mapping.object_members import PLANET_MEMBERS
from rpp.mapping.shared import auth_info, include_elements, prov_metadata
from rpp.mapping.shared.common import parse_rpp
from rpp.schema.validator import validate_request_schema, validate_schema

OBJECT = "planet"


def rpp_to_model(rpp: dict, extensions: tuple[str, ...] = ()) -> Planet:
    """Converts a create request."""
    validate_request_schema("planet.create", rpp, extensions)
    own, members = PLANET_MEMBERS.split(rpp, extensions)
    planet = parse_rpp(RPPPlanet, own)
    return Planet(id=planet.id, type=planet.type, radius=planet.radius, mass=planet.mass,
                  authInfo=auth_info.rpp_to_model(planet.authInfo), extensions=members)


def model_to_rpp(planet: Planet, requested: frozenset[str] = frozenset(), extensions: tuple[str, ...] = ()) -> dict:
    """Converts a planet to its read representation, with the satellites when `requested` names them (onDemand)."""
    rpp = RPPPlanet(
        id=planet.id, type=planet.type, radius=planet.radius, mass=planet.mass,
        authInfo=auth_info.model_to_rpp(planet.authInfo), provMetadata=prov_metadata.model_to_rpp(planet),
        satellite=[RPPSatelliteReference(id=satellite) for satellite in planet.satellites],
    ).to_rpp()
    rpp.update(PLANET_MEMBERS.to_rpp(planet.extensions, extensions))
    validate_schema("planet.read", rpp, extensions)
    return include_elements.visible(OBJECT, rpp, requested)
