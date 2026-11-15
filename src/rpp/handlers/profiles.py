import uuid

from connexion import ProblemException

from core.result.result_code import ResultCode
from rpp.http.context import rpp_profiles
from rpp.http.headers import client_transaction_id, problem_headers, rpp_code, RPP_MEDIA_TYPE
from rpp.http.operation import rpp_operation
from rpp.mapping.profile import profile as profile_mapper


@rpp_operation
def profiles_read(name):
    """The Profile Data Object of an offered profile (json §6.11.1), from the definition and the server's choice. No
    registry command. A name the server does not offer is a 404."""
    catalog = rpp_profiles()
    profile = catalog.by_name(name)
    if profile is None:
        raise ProblemException(
            status=404, title=ResultCode.OBJECT_DOES_NOT_EXIST.value[1],
            detail="The server offers no profile of this name", headers=problem_headers(ResultCode.OBJECT_DOES_NOT_EXIST),
        )
    headers = {
        "Content-Type": RPP_MEDIA_TYPE,
        "RPP-Cltrid": client_transaction_id(),
        "RPP-Svtrid": str(uuid.uuid4()),
        "RPP-Code": rpp_code(ResultCode.COMMAND_COMPLETED_SUCCESSFULLY),
    }
    return profile_mapper.model_to_rpp(profile, profile is catalog.default), 200, headers
