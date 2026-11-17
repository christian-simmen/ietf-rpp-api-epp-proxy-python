from connexion.middleware.swagger_ui import SwaggerUIMiddleware


class SpecSnapshotSwaggerUIMiddleware(SwaggerUIMiddleware):
    """Connexion's Swagger UI middleware, which serves `/openapi.json`, `/openapi.yaml` and `/ui/` from a copy of the
    spec taken when the app starts.

    Connexion's response validation writes `components` into the response schemas of the spec all its middlewares
    share, and the spec served then no longer validates: `/openapi.json` answered 500 after the first request to an
    operation with an inline response schema (#193). The copy is taken before any request, so the document served is
    the one the first request got before.
    """

    def add_api(self, specification, base_path=None, arguments=None, **kwargs) -> None:
        super().add_api(specification.clone(), base_path=base_path, arguments=arguments, **kwargs)
