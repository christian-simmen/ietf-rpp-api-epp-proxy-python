from extensions.planets.core.ports.planets_gateways import PlanetsGateways
from registry_adapter.sqlite.extensions.planets.gateways.sqlite_planet_gateway import SqlitePlanetGateway
from registry_adapter.sqlite.extensions.planets.gateways.sqlite_satellite_gateway import SqliteSatelliteGateway
from registry_adapter.sqlite.sqlite_context import SqliteContext


def gateways(context: SqliteContext) -> PlanetsGateways:
    """The planets and satellites of one client's session."""
    return PlanetsGateways(planets=SqlitePlanetGateway(context), satellites=SqliteSatelliteGateway(context))
