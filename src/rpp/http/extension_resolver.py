from connexion.exceptions import ResolverError
from connexion.resolver import RelativeResolver


class ExtensionResolver(RelativeResolver):
    """Resolves the operationIds of the document relative to `rpp.handlers`, and those of a registered extension as they
    are: its fragment names the function in full, in the handler package it registered."""

    def __init__(self, root_path, handler_packages: tuple[str, ...] = ()):
        super().__init__(root_path)
        self._prefixes = tuple(f"{package}." for package in handler_packages)

    def resolve_operation_id(self, operation):
        operation_id = operation.operation_id
        if operation.router_controller is None and operation_id.startswith(self._prefixes):
            return operation_id
        return super().resolve_operation_id(operation)

    def implements(self, operation_id: str) -> bool:
        """Whether a handler serves the operation: one that none serves answers 501 (`resolver_error`)."""
        name = operation_id if operation_id.startswith(self._prefixes) else f"{self.root_path}.{operation_id}"
        try:
            self.resolve_function_from_operation_id(name)
        except ResolverError:
            return False
        return True
