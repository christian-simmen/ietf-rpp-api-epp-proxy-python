"""The satellites of the planets extension (docs/demo/planets-extension.md), at the paths of its OpenAPI fragment."""
from connexion import request

from core.result.error_response import ErrorResponse
from extensions.planets.core.flows.satellite_flows import create_satellite, patch_satellite, replace_satellite
from extensions.planets.rpp.handlers.planets_gateways import gateways
from extensions.planets.rpp.mapping import satellite_availability, satellite_patch, satellite_replacement, satellites
from rpp.handlers.shared.requested_elements import requested_elements
from rpp.http.context import request_profile
from rpp.http.headers import client_transaction_id, generate_rpp_response_headers
from rpp.http.operation import map_request, require_empty_body, rpp_operation
from rpp.http.problem import raise_registry_error

OBJECT = "satellite"


def _extensions():
    return request_profile().extensions


def _mutation_answer(result, status=200, extra_headers=None):
    """The answer to a mutation: the satellite as read after it, or 202 with no body when that read failed."""
    if isinstance(result, ErrorResponse):
        raise_registry_error(result)
    headers = {**generate_rpp_response_headers(result.mutation), **(extra_headers or {})}
    if result.stored is None:
        return None, 202, headers
    return satellites.model_to_rpp(result.stored, _extensions()), status, headers


@rpp_operation
def satellites_create(body):
    requested_elements(OBJECT)  # a satellite has no data element with onDemand Visibility: any named is refused
    satellite = map_request(satellites.rpp_to_model, body, _extensions())
    result = create_satellite(gateways(), satellite, client_transaction_id())
    return _mutation_answer(result, 201, {"Location": f"{str(request.url).rstrip('/')}/{satellite.id}"})


@rpp_operation
def satellites_read(id):
    requested_elements(OBJECT)
    response = gateways().satellites.info(id, client_transaction_id=client_transaction_id())
    if isinstance(response, ErrorResponse):
        raise_registry_error(response)
    return satellites.model_to_rpp(response.payload, _extensions()), 200, generate_rpp_response_headers(response)


@rpp_operation
def satellites_update(id, body):
    requested_elements(OBJECT)
    wanted = map_request(satellite_replacement.rpp_to_model, id, body, _extensions())
    return _mutation_answer(replace_satellite(gateways(), wanted, client_transaction_id()))


@rpp_operation
def satellites_updatePartial(id, body):
    requested_elements(OBJECT)

    def wanted_from_current(current):
        return map_request(satellite_patch.rpp_to_model_with_current, id, body, current, _extensions())

    return _mutation_answer(patch_satellite(gateways(), id, wanted_from_current, client_transaction_id()))


@rpp_operation
def satellites_delete(id):
    require_empty_body()
    response = gateways().satellites.delete(id, client_transaction_id=client_transaction_id())
    if isinstance(response, ErrorResponse):
        raise_registry_error(response)
    return None, 200, generate_rpp_response_headers(response)


def _availability(id):
    response = gateways().satellites.check(id, client_transaction_id=client_transaction_id())
    if isinstance(response, ErrorResponse):
        raise_registry_error(response)
    return response


@rpp_operation
def satellites_availabilityHead(id):
    response = _availability(id)
    headers = generate_rpp_response_headers(response)
    del headers["Content-Type"]  # the OpenAPI defines no content for HEAD
    return None, 200 if response.payload.available else 404, headers


@rpp_operation
def satellites_availability(id):
    response = _availability(id)
    return (satellite_availability.model_to_rpp(response.payload, _extensions()),
            200 if response.payload.available else 404, generate_rpp_response_headers(response))
