"""The planets of the planets extension (docs/demo/planets-extension.md), at the paths of its OpenAPI fragment."""
from connexion import request

from core.result.error_response import ErrorResponse
from extensions.planets.core.flows.planet_flows import create_planet, patch_planet, replace_planet
from extensions.planets.core.flows.satellite_flows import read_satellite_of_planet
from extensions.planets.rpp.handlers.planets_gateways import gateways
from extensions.planets.rpp.mapping import (
    planet_availability, planet_patch, planet_replacement, planets, satellites,
)
from rpp.handlers.shared.requested_elements import requested_elements
from rpp.http.context import request_profile, response_profile
from rpp.http.headers import client_transaction_id, generate_rpp_response_headers
from rpp.http.operation import map_request, require_empty_body, rpp_operation
from rpp.http.problem import raise_registry_error

OBJECT = "planet"


def _extensions():
    return request_profile().extensions


def _shown():
    """The extensions of the preset of the response: what a response shows."""
    return response_profile().extensions


def _mutation_answer(result, requested, status=200, extra_headers=None):
    """The answer to a mutation: the planet as read after it, or 202 with no body when that read failed."""
    if isinstance(result, ErrorResponse):
        raise_registry_error(result)
    headers = {**generate_rpp_response_headers(result.mutation), **(extra_headers or {})}
    if result.stored is None:
        return None, 202, headers
    return planets.model_to_rpp(result.stored, requested, _shown()), status, headers


@rpp_operation
def planets_create(body):
    requested = requested_elements(OBJECT)
    planet = map_request(planets.rpp_to_model, body, _extensions())
    result = create_planet(gateways(), planet, client_transaction_id())
    return _mutation_answer(result, requested, 201, {"Location": f"{str(request.url).rstrip('/')}/{planet.id}"})


@rpp_operation
def planets_read(id):
    requested = requested_elements(OBJECT)
    response = gateways().planets.info(id, client_transaction_id=client_transaction_id())
    if isinstance(response, ErrorResponse):
        raise_registry_error(response)
    return planets.model_to_rpp(response.payload, requested, _shown()), 200, generate_rpp_response_headers(response)


@rpp_operation
def planets_update(id, body):
    requested = requested_elements(OBJECT)
    wanted = map_request(planet_replacement.rpp_to_model, id, body, _extensions())
    return _mutation_answer(replace_planet(gateways(), wanted, client_transaction_id()), requested)


@rpp_operation
def planets_updatePartial(id, body):
    requested = requested_elements(OBJECT)

    changes = map_request(planet_patch.rpp_to_model, body, _extensions())
    return _mutation_answer(patch_planet(gateways(), id, changes, client_transaction_id()), requested)


@rpp_operation
def planets_delete(id):
    require_empty_body()
    response = gateways().planets.delete(id, client_transaction_id=client_transaction_id())
    if isinstance(response, ErrorResponse):
        raise_registry_error(response)
    return None, 200, generate_rpp_response_headers(response)


def _availability(id):
    response = gateways().planets.check(id, client_transaction_id=client_transaction_id())
    if isinstance(response, ErrorResponse):
        raise_registry_error(response)
    return response


@rpp_operation
def planets_availabilityHead(id):
    response = _availability(id)
    headers = generate_rpp_response_headers(response)
    del headers["Content-Type"]  # the OpenAPI defines no content for HEAD
    return None, 200 if response.payload.available else 404, headers


@rpp_operation
def planets_availability(id):
    response = _availability(id)
    return (planet_availability.model_to_rpp(response.payload, _shown()),
            200 if response.payload.available else 404, generate_rpp_response_headers(response))


@rpp_operation
def planets_satelliteRead(id, satelliteId):
    """A satellite of the planet, at the Direct Access path of the data element `satellite`."""
    requested_elements("satellite")  # a satellite has no data element with onDemand Visibility
    response = read_satellite_of_planet(gateways(), id, satelliteId, client_transaction_id())
    if isinstance(response, ErrorResponse):
        raise_registry_error(response)
    return satellites.model_to_rpp(response.payload, _shown()), 200, generate_rpp_response_headers(response)
