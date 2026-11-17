import jsonschema
from connexion.exceptions import BadRequestProblem
from connexion.validators import JSONRequestBodyValidator

from rpp.http.body_definitions import MARKER
from rpp.http.preset_middleware import REQUEST_SCHEMAS


class RppRequestBodyValidator(JSONRequestBodyValidator):
    """Validates a request body, which an operation may declare optional (a transfer reject).

    A body that stands for a definition (`x-rpp-definition`, #204) is validated with that definition of the preset the request
    is read under, as JSON Schema 2020-12 and without its profiles: a failure is a 400, as the mappers' first step. The profiles
    are the mappers' second step (422 `02308`), which knows what a patch or a replacement results in. Any other body is
    validated with its schema in the OpenAPI document, as Connexion does."""

    _scope = None

    async def wrap_receive(self, receive, *, scope):
        self._scope = scope
        return await super().wrap_receive(receive, scope=scope)

    def _validate(self, body):
        if body is None and not self._required:
            return None
        name = self._schema.get(MARKER)
        schemas = (self._scope or {}).get("extensions", {}).get("connexion_context", {}).get(REQUEST_SCHEMAS)
        if name is None or schemas is None:
            return super()._validate(body)
        if body is None and not self._nullable:
            raise BadRequestProblem("Request body must not be empty")
        try:
            schemas.request.validate(name, body)
        except jsonschema.ValidationError as error:
            # Only the message: the error would print the request, including its authInfo.
            raise BadRequestProblem(detail=error.message) from None
        except ValueError as error:
            raise BadRequestProblem(detail=str(error)) from None
        return None
