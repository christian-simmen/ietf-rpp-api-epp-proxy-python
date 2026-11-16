from typing import Protocol

from core.model.shared.availability import Availability
from core.result.error_response import ErrorResponse
from core.result.operation_response import OperationResponse
from extensions.planets.core.model.satellite import Satellite
from extensions.planets.core.model.satellite_changes import SatelliteChanges
from extensions.planets.core.model.satellite_replacement import SatelliteReplacement


class SatelliteGateway(Protocol):
    """The satellite commands of a backend that holds the demo extension, answering as `PlanetGateway` does."""

    def check(self, id: str, client_transaction_id=None) -> OperationResponse[Availability] | ErrorResponse: ...

    def info(self, id: str, client_transaction_id=None) -> OperationResponse[Satellite] | ErrorResponse: ...

    def create(self, satellite: Satellite, client_transaction_id=None) -> OperationResponse[Satellite] | ErrorResponse:
        """Creates a satellite of a planet the client sponsors."""

    def replace(
        self, replacement: SatelliteReplacement, client_transaction_id=None,
    ) -> OperationResponse[None] | ErrorResponse:
        """A full update, natively: one atomic unit of work that looks the satellite up, checks the sponsor and the state, and
        writes. Answers as `delete` does (not found, authorisation error, a state that prohibits it, a result that breaks
        an invariant)."""

    def patch(
        self, id: str, changes: SatelliteChanges, client_transaction_id=None,
    ) -> OperationResponse[None] | ErrorResponse:
        """A partial update, natively and atomically as `replace`: the members of `changes` are applied to the stored
        satellite in the same unit of work, so no other request comes between the read and the write."""

    def delete(self, id: str, client_transaction_id=None) -> OperationResponse[None] | ErrorResponse: ...
