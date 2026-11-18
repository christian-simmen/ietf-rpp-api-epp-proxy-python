from extensions.planets.core.ports.planets_gateways import EXTENSION_ID, PlanetsGateways
from rpp.http.context import get_backend


def gateways() -> PlanetsGateways:
    """The planets and satellites of the request's session."""
    return get_backend().extension(EXTENSION_ID)
