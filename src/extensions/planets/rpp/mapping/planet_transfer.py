"""The transfer of a planet is the generic Transfer Process Object, as the contact's is: the request carries the
authorisation of the planet in `RPP-Authorization`, and the process is shown as the contact's is (`transferProcess.read`)."""
from core.model.shared.transfer_operation import TransferOperation
from extensions.planets.core.model.planet_transfer import PlanetTransfer
from rpp.dto.rpp_transfer_reject import RPPTransferReject
from rpp.dto.rpp_transfer_request import RPPTransferRequest
from rpp.mapping.contact.contact_transfer_process import model_to_rpp  # noqa: F401 - the same process
from rpp.mapping.shared import rpp_authorization
from rpp.mapping.shared.common import parse_rpp, reject_push, reject_reason
from rpp.schema.validator import validate_request_schema


def request_to_model(id: str, rpp: dict, authorization: str | None) -> PlanetTransfer:
    """Converts a transfer request, with the value of its RPP-Authorization header. Only the pull transfer is supported."""
    validate_request_schema("transferProcess.create", rpp)
    request = parse_rpp(RPPTransferRequest, rpp)
    reject_push(request.transferDir, request.gainingClientId)
    return PlanetTransfer(id=id, operation=TransferOperation.REQUEST, authInfo=rpp_authorization.rpp_to_model(authorization))


def approve_to_model(id: str, rpp: dict | None, authorization: str | None) -> PlanetTransfer:
    """Converts an approve, whose content is optional: None for none."""
    if rpp is not None:
        reject_reason("transferProcess.transferReject", RPPTransferReject, rpp)
    return PlanetTransfer(id=id, operation=TransferOperation.APPROVE, authInfo=rpp_authorization.rpp_to_model(authorization))


def reject_to_model(id: str, rpp: dict | None, authorization: str | None) -> PlanetTransfer:
    """Converts a reject, whose content is optional."""
    if rpp:  # Connexion passes a missing body as an empty dict
        reject_reason("transferProcess.transferReject", RPPTransferReject, rpp)
    return PlanetTransfer(id=id, operation=TransferOperation.REJECT, authInfo=rpp_authorization.rpp_to_model(authorization))
