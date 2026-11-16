from typing import Callable

from core.flows.mutation_result import MutationResult
from core.flows.read_back import read_back
from core.result.error_response import ErrorResponse
from extensions.planets.core.flows.replaced import replaced
from extensions.planets.core.model.planet import Planet
from extensions.planets.core.model.planet_replacement import PlanetReplacement
from extensions.planets.core.ports.planets_gateways import PlanetsGateways


def create_planet(gateways: PlanetsGateways, planet: Planet, client_transaction_id) -> MutationResult | ErrorResponse:
    """Creates a planet and reads it back, as a read shows what the backend stored."""
    created = gateways.planets.create(planet, client_transaction_id=client_transaction_id)
    if isinstance(created, ErrorResponse):
        return created
    return read_back(gateways.planets.info, planet.id, created)


def replace_planet(
    gateways: PlanetsGateways, wanted: PlanetReplacement, client_transaction_id,
) -> MutationResult | ErrorResponse:
    outcome = gateways.planets.replace(wanted, client_transaction_id=client_transaction_id)
    return replaced(gateways.planets.info, wanted.id, outcome)


def patch_planet(
    gateways: PlanetsGateways, planet_id: str, wanted_from_current: Callable[[Planet], PlanetReplacement],
    client_transaction_id,
) -> MutationResult | ErrorResponse:
    """A partial update: the planet is read, `wanted_from_current` applies the patch, and the planet is replaced with
    the result."""
    current = gateways.planets.info(planet_id)
    if isinstance(current, ErrorResponse):
        return current
    outcome = gateways.planets.replace(
        wanted_from_current(current.payload), current=current, client_transaction_id=client_transaction_id)
    return replaced(gateways.planets.info, planet_id, outcome)
