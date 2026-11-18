from core.result.result_code import ResultCode


class Refusal(Exception):
    """Raised inside a unit of work to refuse the command: the unit is rolled back, and the gateway answers with `code`."""

    def __init__(self, code: ResultCode, msg: str):
        super().__init__(msg)
        self.code = code
        self.msg = msg
