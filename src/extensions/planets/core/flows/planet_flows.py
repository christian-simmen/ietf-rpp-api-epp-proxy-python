from core.flows.mutation_result import MutationResult
from core.flows.read_back import read_back
from core.result.error_response import ErrorResponse
from extensions.planets.core.model.planet import Planet
from extensions.planets.core.model.planet_changes import PlanetChanges
from extensions.planets.core.model.planet_replacement import PlanetReplacement
from extensions.planets.core.ports.planets_gateways import PlanetsGateways


def create_planet(gateways: PlanetsGateways, planet: Planet, client_transaction_id) -> MutationResult | ErrorResponse:
    """Creates a planet and reads it back, as a read shows what the backend stored."""
    created = gateways.planets.create(planet, client_transaction_id=client_transaction_id)
    if isinstance(created, ErrorResponse):
        return created
    return read_back(gateways.planets.info, planet.id, created)


def replace_planet(
    gateways: PlanetsGateways, replacement: PlanetReplacement, client_transaction_id,
) -> MutationResult | ErrorResponse:
    """A full update, which the backend applies atomically, and a read back."""
    replaced = gateways.planets.replace(replacement, client_transaction_id=client_transaction_id)
    if isinstance(replaced, ErrorResponse):
        return replaced
    return read_back(gateways.planets.info, replacement.id, replaced)


def patch_planet(
    gateways: PlanetsGateways, planet_id: str, changes: PlanetChanges, client_transaction_id,
) -> MutationResult | ErrorResponse:
    """A partial update, which the backend applies atomically, and a read back."""
    patched = gateways.planets.patch(planet_id, changes, client_transaction_id=client_transaction_id)
    if isinstance(patched, ErrorResponse):
        return patched
    return read_back(gateways.planets.info, planet_id, patched)


