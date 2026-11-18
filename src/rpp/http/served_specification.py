import copy

from connexion.spec import OpenAPISpecification


class ServedSpecification(OpenAPISpecification):
    """The OpenAPI document Connexion serves and does not route with (#204): OpenAPI 3.1, which Connexion's own check knows
    only as 3.0, so it is neither checked against that meta-schema nor has its references resolved. Served as it is given,
    with the base path Connexion gives it (`servers`)."""

    def __init__(self, raw_spec, *, base_uri=""):  # noqa: ARG002 - nothing is resolved, so there is no base URI
        self._raw_spec = copy.deepcopy(raw_spec)
        self._spec = self._raw_spec

    def clone(self):
        return type(self)(self._raw_spec)
