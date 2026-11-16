from typing import Protocol

from core.model.shared.availability import Availability
from core.model.shared.contact_transfer_process import ContactTransferProcess
from core.ports.replace_outcome import ReplaceOutcome
from core.result.error_response import ErrorResponse
from core.result.operation_response import OperationResponse
from extensions.planets.core.model.planet import Planet
from extensions.planets.core.model.planet_replacement import PlanetReplacement
from extensions.planets.core.model.planet_transfer import PlanetTransfer


class PlanetGateway(Protocol):
    """The planet commands of a backend that holds the demo extension, answering as `RequestContactGateway` does. The
    transfer process of a planet is the generic Transfer Process Object, which `ContactTransferProcess` holds."""

    def check(self, id: str, client_transaction_id=None) -> OperationResponse[Availability] | ErrorResponse: ...

    def info(self, id: str, client_transaction_id=None) -> OperationResponse[Planet] | ErrorResponse:
        """The planet; its `authInfo` only for its sponsor."""

    def create(self, planet: Planet, client_transaction_id=None) -> OperationResponse[Planet] | ErrorResponse: ...

    def replace(
        self, wanted: PlanetReplacement, current: OperationResponse[Planet] | None = None, client_transaction_id=None,
    ) -> ReplaceOutcome | ErrorResponse:
        """A full update, by the sponsor only, and not while a transfer is pending. `current` is a read the caller has
        made already."""

    def delete(self, id: str, client_transaction_id=None) -> OperationResponse[None] | ErrorResponse:
        """By the sponsor only, and not while the planet has satellites or a pending transfer."""

    def transfer(
        self, transfer: PlanetTransfer, client_transaction_id=None,
    ) -> OperationResponse[ContactTransferProcess] | ErrorResponse: ...
