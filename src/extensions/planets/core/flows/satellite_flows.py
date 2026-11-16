from typing import Callable

from core.flows.mutation_result import MutationResult
from core.flows.read_back import read_back
from core.result.error_response import ErrorResponse
from core.result.operation_response import OperationResponse
from core.result.result_code import ResultCode
from extensions.planets.core.flows.replaced import replaced
from extensions.planets.core.model.satellite import Satellite
from extensions.planets.core.model.satellite_replacement import SatelliteReplacement
from extensions.planets.core.ports.planets_gateways import PlanetsGateways


def create_satellite(
    gateways: PlanetsGateways, satellite: Satellite, client_transaction_id,
) -> MutationResult | ErrorResponse:
    created = gateways.satellites.create(satellite, client_transaction_id=client_transaction_id)
    if isinstance(created, ErrorResponse):
        return created
    return read_back(gateways.satellites.info, satellite.id, created)


def replace_satellite(
    gateways: PlanetsGateways, wanted: SatelliteReplacement, client_transaction_id,
) -> MutationResult | ErrorResponse:
    outcome = gateways.satellites.replace(wanted, client_transaction_id=client_transaction_id)
    return replaced(gateways.satellites.info, wanted.id, outcome)


def patch_satellite(
    gateways: PlanetsGateways, satellite_id: str, wanted_from_current: Callable[[Satellite], SatelliteReplacement],
    client_transaction_id,
) -> MutationResult | ErrorResponse:
    current = gateways.satellites.info(satellite_id)
    if isinstance(current, ErrorResponse):
        return current
    outcome = gateways.satellites.replace(
        wanted_from_current(current.payload), current=current, client_transaction_id=client_transaction_id)
    return replaced(gateways.satellites.info, satellite_id, outcome)


def read_satellite_of_planet(
    gateways: PlanetsGateways, planet_id: str, satellite_id: str, client_transaction_id,
) -> OperationResponse[Satellite] | ErrorResponse:
    """The satellite at the Direct Access path of its planet: a satellite of another planet does not exist there."""
    satellite = gateways.satellites.info(satellite_id, client_transaction_id=client_transaction_id)
    if isinstance(satellite, ErrorResponse) or satellite.payload.planet == planet_id:
        return satellite
    return ErrorResponse(
        code=ResultCode.OBJECT_DOES_NOT_EXIST,
        msg=f"The planet {planet_id} has no satellite {satellite_id}",
        server_transaction_id=satellite.server_transaction_id,
        client_transaction_id=client_transaction_id,
    )
