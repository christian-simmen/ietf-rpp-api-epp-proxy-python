from contextvars import ContextVar
from dataclasses import dataclass

from rpp.schema.schema_scope import SchemaNotBuilt, SchemaScope


@dataclass(frozen=True)
class RequestSchemas:
    """The schemas of the app one request is handled under: the scope of the preset the request is read under, that of the
    preset the response is under, and every scope of the app (to find the one of a set of extensions)."""
    request: SchemaScope
    response: SchemaScope
    scopes: tuple[SchemaScope, ...]

    def for_extensions(self, extension_ids) -> SchemaScope:
        """The scope without profiles that validates for exactly these extensions, from the app's own presets."""
        ids = tuple(extension_ids)
        found = next((scope for scope in self.scopes if scope.extensions == ids), None)
        if found is None:
            if not ids:
                return SchemaScope.of()
            raise SchemaNotBuilt(f"No preset of the app has the extensions {', '.join(ids)}")
        return found


# The schemas of the request being handled. `rpp_operation` sets it for the duration of a handler, which runs in a thread of
# its own, so mappers (framework-free) validate with the preset of the request without being passed it.
_current: ContextVar[RequestSchemas | None] = ContextVar("rpp_request_schemas", default=None)


def use(schemas: RequestSchemas | None):
    return _current.set(schemas)


def release(token) -> None:
    _current.reset(token)


def current() -> RequestSchemas | None:
    return _current.get()


def profiles_apply() -> bool:
    """Whether the request is under a preset with applicable profiles that have a Profile Schema."""
    schemas = _current.get()
    return bool(schemas and schemas.request.profile_ids)
