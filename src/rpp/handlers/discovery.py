import logging
import uuid
from datetime import datetime, timezone

from connexion import ProblemException

from core.model.shared.discovery import Discovery
from core.model.shared.profile_schema_reference import ProfileSchemaReference
from core.result.result_code import ResultCode
from rpp.http.context import backend_profile, discovery_settings, rpp_profiles
from rpp.http.headers import client_transaction_id, problem_headers, rpp_code, RPP_MEDIA_TYPE
from rpp.http.operation import rpp_operation
from rpp.mapping.discovery import discovery
from rpp.schema.extensions import SERVER_EXTENSIONS
from rpp.schema.profile_schemas import schema_url

logger = logging.getLogger(__name__)

# The RPP version of core §12. The data objects (data-objects §17.2) are the backend's, the profiles (core §12.4) and
# their extensions those the server offers.
RPP_VERSION = "1.0"


@rpp_operation
def discovery_read():
    """The Discovery Data Object: no authentication and no registry command, it comes from configuration and the proxy itself."""
    settings = discovery_settings()
    missing = discovery.invalid_settings(settings)
    if missing:
        logger.warning("Discovery is not configured, missing or invalid: %s", ", ".join(missing))
        raise ProblemException(
            status=500, title=ResultCode.COMMAND_FAILED.value[1], detail="The server is not configured to describe itself",
            headers=problem_headers(ResultCode.COMMAND_FAILED),
        )
    document = Discovery(
        version=RPP_VERSION,
        base_url=settings.rpp_base_url,
        tlds=list(settings.rpp_tlds),
        environment_name=settings.rpp_environment_name,
        environment_status=settings.rpp_environment_status,
        objects=list(backend_profile().objects),
        profiles=[profile.name for profile in rpp_profiles().offered],
        extensions=[*rpp_profiles().extensions(), *SERVER_EXTENSIONS],
        profile_schemas=[ProfileSchemaReference(profile=profile.name, version=profile.version,
                                                url=schema_url(settings.rpp_base_url, profile.name))
                         for profile in rpp_profiles().offered],
        datetime=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    headers = {
        "Content-Type": RPP_MEDIA_TYPE,
        "RPP-Cltrid": client_transaction_id(),
        "RPP-Svtrid": str(uuid.uuid4()),
        "RPP-Code": rpp_code(ResultCode.COMMAND_COMPLETED_SUCCESSFULLY),
    }
    return discovery.model_to_rpp(document), 200, headers
