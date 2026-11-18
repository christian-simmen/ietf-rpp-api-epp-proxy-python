from core.result.error_response import ErrorResponse
from core.result.result_code import ResultCode


class UnsupportedGateway:
    """The gateway of an object the SQLite backend does not hold (the data objects of the drafts). Every command answers
    `UNIMPLEMENTED_OBJECT_SERVICE`. It is never the path that answers a request: the profile has no such object, so the
    profile middleware refuses first (501 `02307`)."""

    def __init__(self, object_name: str):
        self._object_name = object_name

    def __getattr__(self, command: str):
        if command.startswith("_"):
            raise AttributeError(command)

        def refuse(*_args, client_transaction_id=None, **_kwargs):
            return ErrorResponse(
                code=ResultCode.UNIMPLEMENTED_OBJECT_SERVICE, msg=f"The SQLite backend has no {self._object_name} objects",
                server_transaction_id=None, client_transaction_id=client_transaction_id)
        return refuse
