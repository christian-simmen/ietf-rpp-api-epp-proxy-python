from connexion import request
from flask import current_app

from core.capabilities.backend_profile import BackendProfile
from rpp.http.preset_middleware import REQUEST_SCHEMAS, SELECTED_PRESET
from rpp.http.preset_selection import PresetSelection
from rpp.http.request_presets import RequestPresets
from rpp.schema.offered_presets import OfferedPresets
from rpp.schema.preset_schemas import PresetSchemas
from rpp.schema.request_schemas import RequestSchemas

# The key of the token info that holds the request's backend.
TOKEN_BACKEND = "backend"

# The keys of the application configuration that hold what create_app is given.
BACKEND_PROFILE = "RPP_BACKEND_PROFILE"

DISCOVERY_SETTINGS = "RPP_DISCOVERY_SETTINGS"

OFFERED_PRESETS = "RPP_OFFERED_PRESETS"

PRESET_SCHEMAS = "RPP_PRESET_SCHEMAS"

REQUEST_PRESETS = "RPP_REQUEST_PRESETS"


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


def offered_presets() -> OfferedPresets:
    """The RPP presets this application offers."""
    return current_app.config[OFFERED_PRESETS]


def preset_schemas() -> PresetSchemas:
    """The Preset Schemas of the offered presets, built with the app."""
    return current_app.config[PRESET_SCHEMAS]


def preset_selection() -> PresetSelection:
    """The RPP presets of the request, which the preset middleware selected."""
    return request.context[SELECTED_PRESET]


def request_profile() -> BackendProfile:
    """What the backend can hold as the preset the request is read under allows (that of its Content-Type): its
    extensions. Handlers pass this, not `backend_profile()`, to what parses or checks the request (the combined schema,
    the objects)."""
    requests: RequestPresets = current_app.config[REQUEST_PRESETS]
    return requests.profile_of(preset_selection().request)


def response_profile() -> BackendProfile:
    """The same as the preset of the response allows: what a response shows (the extensions of the preset it is under)."""
    requests: RequestPresets = current_app.config[REQUEST_PRESETS]
    return requests.profile_of(preset_selection().response)


def request_schemas() -> RequestSchemas | None:
    """The schemas the request is validated with: those of the preset it is read under, which `rpp_operation` makes the
    mappers' own for the handler. None for an operation without a preset (a document, the router's 404)."""
    return request.context.get(REQUEST_SCHEMAS)


def discovery_settings():
    """What the discovery document states, as configured: rpp_base_url, rpp_tlds, rpp_environment_name and
    rpp_environment_status. None when the application was given none."""
    return current_app.config.get(DISCOVERY_SETTINGS)
