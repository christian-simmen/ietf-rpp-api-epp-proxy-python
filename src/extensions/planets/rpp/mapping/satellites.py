"""The satellite of the planets extension (docs/demo/planets-extension.md)."""
from extensions.planets.core.model.satellite import Satellite
from extensions.planets.rpp.dto.rpp_planet_reference import RPPPlanetReference
from extensions.planets.rpp.dto.rpp_satellite import RPPSatellite
from extensions.planets.rpp.mapping.object_members import SATELLITE_MEMBERS
from rpp.mapping.shared import prov_metadata
from rpp.mapping.shared.common import parse_rpp
from rpp.schema.validator import validate_request_schema, validate_schema

OBJECT = "satellite"


def rpp_to_model(rpp: dict, extensions: tuple[str, ...] = ()) -> Satellite:
    """Converts a create request."""
    validate_request_schema("satellite.create", rpp, extensions)
    own, members = SATELLITE_MEMBERS.split(rpp, extensions)
    satellite = parse_rpp(RPPSatellite, own)
    return Satellite(id=satellite.id, planet=satellite.planet.id, orbitalPeriod=satellite.orbitalPeriod, extensions=members)


def model_to_rpp(satellite: Satellite, extensions: tuple[str, ...] = ()) -> dict:
    rpp = RPPSatellite(
        id=satellite.id, planet=RPPPlanetReference(id=satellite.planet), orbitalPeriod=satellite.orbitalPeriod,
        provMetadata=prov_metadata.model_to_rpp(satellite),
    ).to_rpp()
    rpp.update(SATELLITE_MEMBERS.to_rpp(satellite.extensions, extensions))
    validate_schema("satellite.read", rpp, extensions)
    return rpp
