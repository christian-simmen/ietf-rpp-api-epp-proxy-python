import uuid

from connexion import ProblemException

from core.result.result_code import ResultCode
from rpp.http.context import offered_presets
from rpp.http.headers import RPP_MEDIA_TYPE, client_transaction_id, problem_headers, rpp_code
from rpp.http.operation import rpp_operation
from rpp.mapping.profile import profile as profile_mapper


@rpp_operation
def profiles_read(id):
    """The Profile Data Object of a profile applicable to an offered preset (data-objects §Profile Data Object), from the
    definition. No registry command. An identifier no offered preset has is a 404."""
    presets = offered_presets()
    profile = next((item for item in presets.profiles() if item.id == id), None)
    if profile is None:
        raise ProblemException(
            status=404, title=ResultCode.OBJECT_DOES_NOT_EXIST.value[1],
            detail="No preset of this server has a profile of this identifier",
            headers=problem_headers(ResultCode.OBJECT_DOES_NOT_EXIST),
        )
    headers = {
        "Content-Type": RPP_MEDIA_TYPE,
        "RPP-Cltrid": client_transaction_id(),
        "RPP-Svtrid": str(uuid.uuid4()),
        "RPP-Code": rpp_code(ResultCode.COMMAND_COMPLETED_SUCCESSFULLY),
    }
    return profile_mapper.model_to_rpp(profile, presets.flattening), 200, headers
