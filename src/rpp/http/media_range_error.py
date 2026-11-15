from core.result.result_code import ResultCode


class MediaRangeError(ValueError):
    """An Accept or Content-Type value is refused: `code` is the RPP client error code (core §12.4), the message goes in
    the detail."""

    def __init__(self, code: ResultCode, message: str):
        super().__init__(message)
        self.code = code
