"""The satellite of the planets extension (docs/demo/planets-extension.md)."""
from extensions.planets.core.model.satellite import Satellite
from extensions.planets.rpp.dto.rpp_planet_reference import RPPPlanetReference
from extensions.planets.rpp.dto.rpp_satellite import RPPSatellite
from rpp.mapping.shared import prov_metadata
from rpp.mapping.shared.common import parse_rpp
from rpp.schema.validator import validate_schema

OBJECT = "satellite"


def rpp_to_model(rpp: dict, extensions: tuple[str, ...] = ()) -> Satellite:
    """Converts a create request."""
    validate_schema("satellite.create", rpp, extensions)
    satellite = parse_rpp(RPPSatellite, rpp)
    return Satellite(id=satellite.id, planet=satellite.planet.id, orbitalPeriod=satellite.orbitalPeriod)


def model_to_rpp(satellite: Satellite, extensions: tuple[str, ...] = ()) -> dict:
    rpp = RPPSatellite(
        id=satellite.id, planet=RPPPlanetReference(id=satellite.planet), orbitalPeriod=satellite.orbitalPeriod,
        provMetadata=prov_metadata.model_to_rpp(satellite),
    ).to_rpp()
    validate_schema("satellite.read", rpp, extensions)
    return rpp
