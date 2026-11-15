from connexion import request
from flask import current_app

from core.capabilities.backend_profile import BackendProfile
from rpp.http.profile_middleware import SELECTED_PROFILE
from rpp.http.request_profiles import RequestProfiles
from rpp.schema.rpp_profile import RppProfile
from rpp.schema.rpp_profiles import RppProfiles

# The key of the token info that holds the request's backend.
TOKEN_BACKEND = "backend"

# The keys of the application configuration that hold what create_app is given.
BACKEND_PROFILE = "RPP_BACKEND_PROFILE"

DISCOVERY_SETTINGS = "RPP_DISCOVERY_SETTINGS"

RPP_PROFILES = "RPP_PROFILES"

REQUEST_PROFILES = "RPP_REQUEST_PROFILES"


def get_backend():
    """
    Get the registry backend of the request's session from the request context.
    """
    if "token_info" not in request.context or TOKEN_BACKEND not in request.context["token_info"]:
        raise ValueError("Registry backend not found in request context")
    return request.context["token_info"][TOKEN_BACKEND]


def backend_profile() -> BackendProfile:
    """What the backend of this application can hold."""
    return current_app.config[BACKEND_PROFILE]


def rpp_profiles() -> RppProfiles:
    """The RPP profiles this application offers."""
    return current_app.config[RPP_PROFILES]


def selected_profile() -> RppProfile:
    """The RPP profile of the request, which the profile middleware selected."""
    return request.context[SELECTED_PROFILE]


def request_profile() -> BackendProfile:
    """What the backend can hold as the request's profile allows: its extensions and its data objects. Handlers pass
    this, not `backend_profile()`, to what depends on the profile (the combined schema, the objects)."""
    requests: RequestProfiles = current_app.config[REQUEST_PROFILES]
    return requests.of(selected_profile())


def discovery_settings():
    """What the discovery document states, as configured: rpp_base_url, rpp_tlds, rpp_environment_name and
    rpp_environment_status. None when the application was given none."""
    return current_app.config.get(DISCOVERY_SETTINGS)
