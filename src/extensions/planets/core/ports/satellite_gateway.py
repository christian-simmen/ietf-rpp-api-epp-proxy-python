from typing import Protocol

from core.model.shared.availability import Availability
from core.ports.replace_outcome import ReplaceOutcome
from core.result.error_response import ErrorResponse
from core.result.operation_response import OperationResponse
from extensions.planets.core.model.satellite import Satellite
from extensions.planets.core.model.satellite_replacement import SatelliteReplacement


class SatelliteGateway(Protocol):
    """The satellite commands of a backend that holds the demo extension, answering as `PlanetGateway` does."""

    def check(self, id: str, client_transaction_id=None) -> OperationResponse[Availability] | ErrorResponse: ...

    def info(self, id: str, client_transaction_id=None) -> OperationResponse[Satellite] | ErrorResponse: ...

    def create(self, satellite: Satellite, client_transaction_id=None) -> OperationResponse[Satellite] | ErrorResponse:
        """Creates a satellite of a planet the client sponsors."""

    def replace(
        self, wanted: SatelliteReplacement, current: OperationResponse[Satellite] | None = None,
        client_transaction_id=None,
    ) -> ReplaceOutcome | ErrorResponse:
        """A full update, by the sponsor only, and not while its planet has a pending transfer."""

    def delete(self, id: str, client_transaction_id=None) -> OperationResponse[None] | ErrorResponse: ...
