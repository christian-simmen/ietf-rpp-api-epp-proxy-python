import uuid

from connexion import ProblemException
from flask import request as flask_request

from core.result.result_code import ResultCode
from rpp.handlers.shared.requested_elements import requested_elements
from rpp.http.context import offered_presets, preset_schemas
from rpp.http.headers import RPP_MEDIA_TYPE, client_transaction_id, problem_headers, rpp_code
from rpp.http.media_range_error import MediaRangeError
from rpp.http.native_accept import accepts
from rpp.http.operation import rpp_operation
from rpp.mapping.preset import preset as preset_mapper
from rpp.schema.preset_schemas import MEDIA_TYPE
from rpp.schema.schema_scope import SchemaScope

OBJECT = "preset"


def _offered(identifier):
    preset = offered_presets().by_id(identifier)
    if preset is None:
        raise ProblemException(
            status=404, title=ResultCode.OBJECT_DOES_NOT_EXIST.value[1],
            detail="The server offers no preset of this identifier", headers=problem_headers(ResultCode.OBJECT_DOES_NOT_EXIST),
        )
    return preset


@rpp_operation
def presets_read(id):
    """The Preset Data Object of an offered preset (data-objects §Preset Data Object), from the definition and the server's
    choice. No registry command. An identifier the server does not offer is a 404. The onDemand `schema` is embedded when
    the request includes it."""
    requested = requested_elements(OBJECT)
    preset = _offered(id)
    schema = preset_schemas().document_of(preset) if "schema" in requested else None
    headers = {
        "Content-Type": RPP_MEDIA_TYPE,
        "RPP-Cltrid": client_transaction_id(),
        "RPP-Svtrid": str(uuid.uuid4()),
        "RPP-Code": rpp_code(ResultCode.COMMAND_COMPLETED_SUCCESSFULLY),
    }
    return preset_mapper.model_to_rpp(preset, SchemaScope.of(), schema), 200, headers


def _check_accept():
    """The document is `application/schema+json`: an `Accept` that does not allow it is a 406 (core §Native Media Types)."""
    try:
        allowed = accepts(flask_request.headers.getlist("Accept"), MEDIA_TYPE)
    except MediaRangeError as error:
        raise ProblemException(status=400, title=error.code.value[1], detail=str(error),
                               headers={**problem_headers(error.code), "Vary": "Accept"}) from None
    if not allowed:
        code = ResultCode.PARAMETER_VALUE_RANGE_ERROR
        raise ProblemException(status=406, title=code.value[1],
                               detail=f"The schema of a preset is {MEDIA_TYPE}, which the Accept field does not allow",
                               headers={**problem_headers(code), "Vary": "Accept"})


@rpp_operation
def presets_schemaRead(id):
    """The Preset Schema of an offered preset (json §Preset Schema), built when the app was built. A value in its native media
    type, not an RPP operation: no authentication, no registry command, no preset selection, and `RPP-Cltrid` is echoed when
    sent. An identifier the server does not offer is a 404."""
    _check_accept()
    document = preset_schemas().document_of(_offered(id))
    headers = {
        "Content-Type": MEDIA_TYPE,
        "Vary": "Accept",
        "RPP-Svtrid": str(uuid.uuid4()),
        "RPP-Code": rpp_code(ResultCode.COMMAND_COMPLETED_SUCCESSFULLY),
    }
    if client_transaction_id():
        headers["RPP-Cltrid"] = client_transaction_id()
    return document, 200, headers
