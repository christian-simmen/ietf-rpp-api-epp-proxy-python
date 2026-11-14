from core.result.error_response import ErrorResponse
from core.result.result_code import ResultCode


class EppRequestContactGateway:
    """EPP has no request contacts (RFC 5733 knows only contacts with postal data). Every command answers
    `UNIMPLEMENTED_COMMAND`, the port's convention for a command the backend lacks."""

    @staticmethod
    def _lacking(client_transaction_id):
        return ErrorResponse(code=ResultCode.UNIMPLEMENTED_COMMAND, msg="EPP has no request contacts",
                             server_transaction_id=None, client_transaction_id=client_transaction_id)

    def check(self, id, client_transaction_id=None):
        return self._lacking(client_transaction_id)

    def info(self, id, client_transaction_id=None):
        return self._lacking(client_transaction_id)

    def create(self, contact, client_transaction_id=None):
        return self._lacking(client_transaction_id)

    def replace(self, wanted, current=None, client_transaction_id=None):
        return self._lacking(client_transaction_id)

    def delete(self, id, client_transaction_id=None):
        return self._lacking(client_transaction_id)
