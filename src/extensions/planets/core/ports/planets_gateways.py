from dataclasses import dataclass

from extensions.planets.core.ports.planet_gateway import PlanetGateway
from extensions.planets.core.ports.satellite_gateway import SatelliteGateway

EXTENSION_ID = "org.example.rpp.extension.planets"


@dataclass(frozen=True)
class PlanetsGateways:
    """What a backend that holds the planets extension gives for it (`RegistryBackend.extension(EXTENSION_ID)`)."""
    planets: PlanetGateway
    satellites: SatelliteGateway
