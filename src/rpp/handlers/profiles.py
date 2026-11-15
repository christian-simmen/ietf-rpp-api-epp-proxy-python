import uuid

from connexion import ProblemException
from flask import request as flask_request

from core.result.result_code import ResultCode
from rpp.http.context import profile_schemas, rpp_profiles
from rpp.http.media_range_error import MediaRangeError
from rpp.http.profile_schema_path import accepts_schema
from rpp.http.headers import client_transaction_id, problem_headers, rpp_code, RPP_MEDIA_TYPE
from rpp.http.operation import rpp_operation
from rpp.mapping.profile import profile as profile_mapper
from rpp.schema.profile_schemas import MEDIA_TYPE


def _offered(name):
    profile = rpp_profiles().by_name(name)
    if profile is None:
        raise ProblemException(
            status=404, title=ResultCode.OBJECT_DOES_NOT_EXIST.value[1],
            detail="The server offers no profile of this name", headers=problem_headers(ResultCode.OBJECT_DOES_NOT_EXIST),
        )
    return profile


@rpp_operation
def profiles_read(name):
    """The Profile Data Object of an offered profile (json §6.11.1), from the definition and the server's choice. No
    registry command. A name the server does not offer is a 404."""
    profile = _offered(name)
    headers = {
        "Content-Type": RPP_MEDIA_TYPE,
        "RPP-Cltrid": client_transaction_id(),
        "RPP-Svtrid": str(uuid.uuid4()),
        "RPP-Code": rpp_code(ResultCode.COMMAND_COMPLETED_SUCCESSFULLY),
    }
    return profile_mapper.model_to_rpp(profile, profile is rpp_profiles().default), 200, headers


def _check_accept():
    """The document is `application/schema+json`: an `Accept` that does not allow it is a 406 (core §13)."""
    try:
        allowed = accepts_schema(flask_request.headers.getlist("Accept"))
    except MediaRangeError as error:
        raise ProblemException(status=400, title=error.code.value[1], detail=str(error),
                               headers={**problem_headers(error.code), "Vary": "Accept"}) from None
    if not allowed:
        code = ResultCode.PARAMETER_VALUE_RANGE_ERROR
        raise ProblemException(status=406, title=code.value[1],
                               detail=f"The schema of a profile is {MEDIA_TYPE}, which the Accept field does not allow",
                               headers={**problem_headers(code), "Vary": "Accept"})


@rpp_operation
def profiles_schemaRead(name):
    """The effective JSON Schema of an offered profile (json §7.2), built when the app was built. A document, not an RPP
    operation: no authentication, no registry command, no profile selection, and `RPP-Cltrid` is echoed when sent. A
    name the server does not offer is a 404."""
    _check_accept()
    document = profile_schemas().of(_offered(name))
    headers = {
        "Content-Type": MEDIA_TYPE,
        "Vary": "Accept",
        "RPP-Svtrid": str(uuid.uuid4()),
        "RPP-Code": rpp_code(ResultCode.COMMAND_COMPLETED_SUCCESSFULLY),
    }
    if client_transaction_id():
        headers["RPP-Cltrid"] = client_transaction_id()
    return document, 200, headers
