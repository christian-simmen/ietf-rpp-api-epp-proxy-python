from connexion.middleware.swagger_ui import SwaggerUIMiddleware

from rpp.http.served_specification import ServedSpecification


class ServedDocumentSwaggerUIMiddleware(SwaggerUIMiddleware):
    """Connexion's Swagger UI middleware, which serves `/openapi.json`, `/openapi.yaml` and `/ui/` from the document it is given
    (`served_document`, OpenAPI 3.1, #204) instead of the spec Connexion routes with.

    The document is its own, made when the app is built: Connexion's response validation, which writes `components` into the
    response schemas of the spec its middlewares share, does not reach it (#193). `create_app` gives it per app
    (`functools.partial`), as Connexion builds a middleware with the app alone."""

    def __init__(self, app, document: dict):
        super().__init__(app)
        self._document = document

    def add_api(self, specification, base_path=None, arguments=None, **kwargs) -> None:  # noqa: ARG002 - served is its own
        super().add_api(ServedSpecification(self._document), base_path=base_path, arguments=arguments, **kwargs)
