from core.result.error_response import ErrorResponse
from core.result.operation_response import OperationResponse
from core.result.result_code import ResultCode
from registry_adapter.sqlite.gateways.refusal import Refusal
from registry_adapter.sqlite.member_refused import MemberRefused
from registry_adapter.sqlite.clock import new_server_transaction_id
from registry_adapter.sqlite.sqlite_context import SqliteContext

SUCCESS = "Command completed successfully"


class SqliteGateway:
    """The base of the gateways of the demo backend: they answer as the gateways of the protocols do, with a server
    transaction id of their own, and know the client of the session."""

    def __init__(self, context: SqliteContext):
        self._context = context

    @property
    def sponsor_id(self) -> str:
        return self._context.sponsor_id

    def _ok(self, payload, client_transaction_id, code: ResultCode = ResultCode.COMMAND_COMPLETED_SUCCESSFULLY,
            msg: str = SUCCESS) -> OperationResponse:
        return OperationResponse(code=code, msg=msg, server_transaction_id=new_server_transaction_id(),
                                 client_transaction_id=client_transaction_id, payload=payload)

    def _refused(self, code: ResultCode, msg: str, client_transaction_id) -> ErrorResponse:
        return ErrorResponse(code=code, msg=msg, server_transaction_id=new_server_transaction_id(),
                             client_transaction_id=client_transaction_id)

    def _hooks_for(self, target: str):
        """The hooks of the extensions that add members to the objects of `target`, by extension id."""
        return self._context.hooks.get(target, {})

    def _hook(self, target: str, extension_id: str):
        hook = self._hooks_for(target).get(extension_id)
        if hook is None:
            raise Refusal(ResultCode.UNIMPLEMENTED_EXTENSION, f"The backend holds no members of {extension_id}")
        return hook

    def _replace_members(self, session, target: str, object_id: str, members) -> None:
        """A full update of the members the extensions add: one a hook holds and `members` lacks is removed, and members of
        an extension without a hook are refused."""
        hooks = self._hooks_for(target)
        for extension_id in members.keys() - hooks.keys():
            self._hook(target, extension_id)
        for extension_id, hook in hooks.items():
            hook.replace(session, object_id, members.get(extension_id))

    def _guarded(self, client_transaction_id, work):
        """Runs `work`, a unit of work that answers or raises `Refusal` (or `MemberRefused` for a hook): a refusal has rolled
        the unit back, and answers as the refusal says."""
        try:
            return work()
        except Refusal as refusal:
            return self._refused(refusal.code, refusal.msg, client_transaction_id)
        except MemberRefused as refusal:
            return self._refused(ResultCode.PARAMETER_VALUE_RANGE_ERROR, str(refusal), client_transaction_id)
