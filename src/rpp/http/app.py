import copy
from functools import cache
from pathlib import Path

import yaml
from connexion import FlaskApp
from connexion.datastructures import MediaTypeDict
from connexion.exceptions import ProblemException
from connexion.middleware import ConnexionMiddleware, MiddlewarePosition
from connexion.middleware.swagger_ui import SwaggerUIMiddleware
from connexion.validators import VALIDATOR_MAP
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware

from core.capabilities.backend_profile import BackendProfile
from rpp.http.context import BACKEND_PROFILE, DISCOVERY_SETTINGS, PROFILE_SCHEMAS, REQUEST_PROFILES, RPP_PROFILES
from rpp.http.middleware.body_buffering_middleware import BodyBufferingMiddleware
from rpp.http.problem import handle_http_exception, handle_rpp_error
from rpp.http.profile_middleware import ProfileMiddleware
from rpp.http.profile_signalling import HEADER_SIGNALLING, profile_signalling
from rpp.http.request_profiles import RequestProfiles
from rpp.http.middleware.line_feed_path_middleware import LineFeedPathMiddleware
from rpp.http.middleware.spec_snapshot_swagger_ui_middleware import SpecSnapshotSwaggerUIMiddleware
from rpp.http.security.bearer_refusing_security_handler import BearerRefusingSecurityHandler
from rpp.http.security.session_security_handler import SessionSecurityHandler
from rpp.http.validators.rpp_request_body_validator import RppRequestBodyValidator
from rpp.http.validators.rpp_response_body_validator import RppResponseBodyValidator
from registration import ExtensionRegistry
from rpp.http.extension_paths import add_extension_paths, add_registered_paths
from rpp.http.extension_resolver import ExtensionResolver
from rpp.http.profile_schema_path import add_profile_schema_path
from rpp.schema.extensions import check_known
from rpp.schema.https_url import https_url
from rpp.schema.profile_schemas import ProfileSchemas
from rpp.schema.rpp_profiles import RppProfiles

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
        signalling: How a client names the profile of a request (`rpp_profile_signalling`): `header` or `media-type`.
        registry: The extensions this app registered (`rpp_extensions`): their paths and handlers are the app's, and
            only its. Without it the app is the drafts' and the extensions of the proxy's own.
    """
    registry = registry or ExtensionRegistry()
    check_known(profile.extensions)
    profiles = RppProfiles.build(profile.profiles, profile.default_profile, profile.extensions)
    request_profiles = RequestProfiles(profile, profiles)
    # The effective schemas are built here, once, and only read by a request. A base URL that discovery would refuse is
    # no public URL: the documents then have no `$id`.
    profile_schemas = ProfileSchemas(profiles, public_base_url(discovery_settings))
    app = FlaskApp(
        __name__,
        security_map={"basic": lambda: SessionSecurityHandler(sessions), "bearer": BearerRefusingSecurityHandler},
        # The spec is served from a copy taken at start, which response validation does not change (#193).
        middlewares=[SpecSnapshotSwaggerUIMiddleware if middleware is SwaggerUIMiddleware else middleware
                     for middleware in ConnexionMiddleware.default_middlewares],
    )
    app.add_middleware(LineFeedPathMiddleware, position=MiddlewarePosition.BEFORE_ROUTING)
    app.add_middleware(BodyBufferingMiddleware, position=MiddlewarePosition.BEFORE_VALIDATION)
    app.add_middleware(ProfileMiddleware, position=MiddlewarePosition.BEFORE_VALIDATION,
                       signalling=profile_signalling(signalling, profiles), request_profiles=request_profiles,
                       extensions=profiles.extensions())
    app.add_middleware(
        CORSMiddleware,
        position=MiddlewarePosition.BEFORE_EXCEPTION,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # connexion changes the spec it is given, so each app gets its own copy.
    spec = add_profile_schema_path(add_registered_paths(
        add_extension_paths(copy.deepcopy(parsed_spec()), profiles.extensions()), registry))
    app.add_api(spec, resolver=ExtensionResolver('rpp.handlers', registry.handler_packages()), resolver_error=501,
                validate_responses=True, options={"swagger_ui": True, "serve_spec": True},
                validator_map={
                    "body": MediaTypeDict({**VALIDATOR_MAP["body"], "*/*json": RppRequestBodyValidator}),
                    "response": MediaTypeDict({"*/*json": RppResponseBodyValidator}),
                })
    app.app.config[DISCOVERY_SETTINGS] = discovery_settings
    app.app.config[BACKEND_PROFILE] = profile
    app.app.config[RPP_PROFILES] = profiles
    app.app.config[PROFILE_SCHEMAS] = profile_schemas
    app.app.config[REQUEST_PROFILES] = request_profiles
    app.add_error_handler(ProblemException, handle_rpp_error)
    app.add_error_handler(HTTPException, handle_http_exception)

    return app
