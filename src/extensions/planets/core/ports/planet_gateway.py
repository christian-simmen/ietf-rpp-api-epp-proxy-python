from typing import Protocol

from core.model.shared.availability import Availability
from core.model.shared.contact_transfer_process import ContactTransferProcess
from core.result.error_response import ErrorResponse
from core.result.operation_response import OperationResponse
from extensions.planets.core.model.planet import Planet
from extensions.planets.core.model.planet_changes import PlanetChanges
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
        self, replacement: PlanetReplacement, client_transaction_id=None,
    ) -> OperationResponse[None] | ErrorResponse:
        """A full update, natively: one atomic unit of work that looks the planet up, checks the sponsor and the state, and
        writes. Answers as `delete` does (not found, authorisation error, a state that prohibits it, a result that breaks
        an invariant)."""

    def patch(
        self, id: str, changes: PlanetChanges, client_transaction_id=None,
    ) -> OperationResponse[None] | ErrorResponse:
        """A partial update, natively and atomically as `replace`: the members of `changes` are applied to the stored
        planet in the same unit of work, so no other request comes between the read and the write."""

    def delete(self, id: str, client_transaction_id=None) -> OperationResponse[None] | ErrorResponse:
        """By the sponsor only, and not while the planet has satellites or a pending transfer."""

    def transfer(
        self, transfer: PlanetTransfer, client_transaction_id=None,
    ) -> OperationResponse[ContactTransferProcess] | ErrorResponse: ...
