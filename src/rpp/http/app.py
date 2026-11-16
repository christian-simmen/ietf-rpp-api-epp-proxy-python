import copy
from functools import cache
from pathlib import Path

import yaml
from connexion import FlaskApp
from connexion.datastructures import MediaTypeDict
from connexion.exceptions import ProblemException
from connexion.middleware import MiddlewarePosition
from connexion.validators import VALIDATOR_MAP
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware

from core.capabilities.backend_profile import BackendProfile
from rpp.http.context import BACKEND_PROFILE, DISCOVERY_SETTINGS, OFFERED_PRESETS, PRESET_SCHEMAS, REQUEST_PRESETS
from rpp.http.middleware.body_buffering_middleware import BodyBufferingMiddleware
from rpp.http.problem import handle_http_exception, handle_rpp_error
from rpp.http.preset_middleware import PresetMiddleware
from rpp.http.preset_signalling import HEADER_SIGNALLING, preset_signalling
from rpp.http.request_presets import RequestPresets
from rpp.http.middleware.line_feed_path_middleware import LineFeedPathMiddleware
from rpp.http.security.session_security_handler import SessionSecurityHandler
from rpp.http.validators.rpp_request_body_validator import RppRequestBodyValidator
from rpp.http.validators.rpp_response_body_validator import RppResponseBodyValidator
from registration import ExtensionRegistry
from rpp.http.extension_paths import add_extension_paths, add_registered_paths
from rpp.http.extension_resolver import ExtensionResolver
from rpp.schema.extensions import EXTENSIONS, check_known
from rpp.schema.https_url import https_url
from rpp.schema.definitions import Definitions
from rpp.schema.offered_presets import OfferedPresets
from rpp.schema.preset_schemas import PresetSchemas

OPENAPI_SPEC = Path(__file__).parent.parent / "openapi.yaml"


@cache
def parsed_spec() -> dict:
    """
    The OpenAPI document, parsed once per process with libyaml, because parsing it takes most of the time an app
    takes to build (#112). Callers get it shared: copy it before handing it on.
    """
    with OPENAPI_SPEC.open("rb") as spec:
        return yaml.load(spec, Loader=yaml.CSafeLoader)


def public_base_url(discovery_settings) -> str | None:
    """The base URL the discovery document states, None where there is none to state (unset, not an acceptable https URL:
    no userinfo, query or fragment, or settings that cannot be read: discovery answers that at request time). An unauthenticated
    endpoint publishes it in a `$id`, so it must be one discovery would state."""
    try:
        url = getattr(discovery_settings, "rpp_base_url", None)
    except Exception:  # noqa: BLE001 - settings are read by the request that needs them
        return None
    return url if https_url(url) else None


def create_app(sessions, profile: BackendProfile, discovery_settings=None, signalling=HEADER_SIGNALLING,
               registry: ExtensionRegistry | None = None):
    """
    Builds the application.

    Args:
        sessions: The `SessionPool`, which gives the registry backend of the request's user, or None to reject the
            request.
        profile: What the backend can hold, which the mappers check, refusals name and discovery states.
        discovery_settings: Has rpp_base_url, rpp_tlds, rpp_environment_name and
            rpp_environment_status, which the discovery document states.
        signalling: How a client names the preset of a request (`rpp_preset_signalling`): `header` or `media-type`.
        registry: The extensions this app registered (`rpp_extensions`): their paths and handlers are the app's, and
            only its. Without it the app is the drafts' and the extensions of the proxy's own.
    """
    registry = registry or ExtensionRegistry()
    check_known(profile.extensions)
    definitions = Definitions.load(registry, EXTENSIONS)
    presets = OfferedPresets.build(definitions, profile.presets, profile.default_preset, profile.bound_profiles,
                                   profile.extensions)
    # The Preset Schemas and their validators are built here, once, per app, and only read by a request. A base URL that
    # discovery would refuse is no public URL: the documents then have no `$id`.
    preset_schemas = PresetSchemas(presets, public_base_url(discovery_settings))
    request_presets = RequestPresets(profile, presets, preset_schemas)
    app = FlaskApp(
        __name__,
        security_map={"basic": lambda: SessionSecurityHandler(sessions)},
    )
    app.add_middleware(LineFeedPathMiddleware, position=MiddlewarePosition.BEFORE_ROUTING)
    app.add_middleware(BodyBufferingMiddleware, position=MiddlewarePosition.BEFORE_VALIDATION)
    app.add_middleware(PresetMiddleware, position=MiddlewarePosition.BEFORE_VALIDATION,
                       signalling=preset_signalling(signalling, presets), request_presets=request_presets,
                       extensions=presets.extension_ids())
    app.add_middleware(
        CORSMiddleware,
        position=MiddlewarePosition.BEFORE_EXCEPTION,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # connexion changes the spec it is given, so each app gets its own copy.
    spec = add_registered_paths(add_extension_paths(copy.deepcopy(parsed_spec()), presets.extension_ids()), registry)
    app.add_api(spec, resolver=ExtensionResolver('rpp.handlers', registry.handler_packages()), resolver_error=501,
                validate_responses=True, options={"swagger_ui": True, "serve_spec": True},
                validator_map={
                    "body": MediaTypeDict({**VALIDATOR_MAP["body"], "*/*json": RppRequestBodyValidator}),
                    "response": MediaTypeDict({"*/*json": RppResponseBodyValidator}),
                })
    app.app.config[DISCOVERY_SETTINGS] = discovery_settings
    app.app.config[BACKEND_PROFILE] = profile
    app.app.config[OFFERED_PRESETS] = presets
    app.app.config[PRESET_SCHEMAS] = preset_schemas
    app.app.config[REQUEST_PRESETS] = request_presets
    app.add_error_handler(ProblemException, handle_rpp_error)
    app.add_error_handler(HTTPException, handle_http_exception)

    return app
