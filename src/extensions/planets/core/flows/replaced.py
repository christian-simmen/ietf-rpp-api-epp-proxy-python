from typing import Callable

from core.flows.mutation_result import MutationResult
from core.flows.read_back import read_back
from core.result.error_response import ErrorResponse


def replaced(info: Callable, key: str, outcome) -> MutationResult | ErrorResponse:
    """The object read back after a full update, or as read when nothing changed (core §16.8 asks for a 200 then).
    The gateway has checked the sponsor of either."""
    if isinstance(outcome, ErrorResponse):
        return outcome
    if outcome.unchanged:
        return MutationResult(mutation=outcome.current, stored=outcome.current.payload)
    return read_back(info, key, outcome.mutation)
