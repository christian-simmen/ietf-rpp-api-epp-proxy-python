"""The transfer of a planet, with the operations of the generic Transfer Process Object."""
from extensions.planets.core.ports.planets_gateways import EXTENSION_ID
from extensions.planets.core.model.planet_transfer import PlanetTransfer
from extensions.planets.rpp.mapping import planet_transfer
from rpp.handlers.shared.transfer_handlers import TransferHandlers
from rpp.http.operation import rpp_operation

_handlers = TransferHandlers(
    gateway_of=lambda backend: backend.extension(EXTENSION_ID).planets,
    operations_of=lambda profile: profile.planet.processes.transfer.operations,
    create_mapper=planet_transfer.request_to_model,
    approve_mapper=planet_transfer.approve_to_model,
    reject_mapper=planet_transfer.reject_to_model,
    response_mapper=planet_transfer.model_to_rpp,
    make_transfer=lambda id, operation, auth_info: PlanetTransfer(id=id, operation=operation, authInfo=auth_info),
)


@rpp_operation
def planetTransferProcesses_transferCreate(id, body):
    return _handlers.create(id, body)


@rpp_operation
def planetTransferProcesses_transferRead(id):
    return _handlers.read(id)


@rpp_operation
def planetTransferProcesses_transferDelete(id):
    return _handlers.delete(id)


@rpp_operation
def planetTransferProcesses_transferApprove(id):
    return _handlers.approve(id)


@rpp_operation
def planetTransferProcesses_transferReject(id, body=None):
    return _handlers.reject(id, body)
