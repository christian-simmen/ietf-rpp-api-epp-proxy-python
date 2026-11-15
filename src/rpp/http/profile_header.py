"""The `RPP-Profile` header field of core §14.2: an RFC 9651 Dictionary with a `profile` member (a Token) that carries
a `version` parameter (a Decimal), and the media type parameters that mean the other signalling method.

Parsing is `http-sfv`'s, which implements RFC 9651. This module enforces what §14.2 adds. Other members and parameters
are ignored (gap: §14.2 does not say what a server does with them).
"""
import re
from decimal import Decimal

import http_sfv

from core.result.result_code import ResultCode
from rpp.schema.rpp_profile import RppProfile

HEADER = "RPP-Profile"


class ProfileHeaderError(ValueError):
    """The header is refused: `code` is the RPP client error code (core §12.4), the message goes in the detail."""

    def __init__(self, code: ResultCode, message: str):
        super().__init__(message)
        self.code = code


def parse(values: list[str]) -> tuple[str, Decimal] | None:
    """The profile name and version a request names, None when it has no `RPP-Profile` header."""
    if not values:
        return None
    # RFC 9651 §4.2: the field lines are combined with a comma into one Dictionary, where a repeated key is the last.
    # An empty line is an empty Dictionary, which http-sfv does not parse, and adds nothing.
    combined = ", ".join(value.strip(" \t") for value in values if value.strip(" \t"))
    if not combined:
        raise ProfileHeaderError(ResultCode.REQUIRED_PARAMETER_MISSING, f"{HEADER} has no profile member")
    dictionary = http_sfv.Dictionary()
    try:
        dictionary.parse(combined.encode("ascii"))
    except (ValueError, UnicodeEncodeError):
        raise ProfileHeaderError(
            ResultCode.PARAMETER_VALUE_SYNTAX_ERROR, f"{HEADER} is not a Structured Field Dictionary") from None
    member = dictionary.get("profile")
    if member is None:
        raise ProfileHeaderError(ResultCode.REQUIRED_PARAMETER_MISSING, f"{HEADER} has no profile member")
    if not isinstance(member, http_sfv.Item) or not isinstance(member.value, http_sfv.Token):
        raise ProfileHeaderError(ResultCode.PARAMETER_VALUE_SYNTAX_ERROR, f"The profile of {HEADER} is not a token")
    if "version" not in member.params:
        raise ProfileHeaderError(
            ResultCode.REQUIRED_PARAMETER_MISSING, f"The profile of {HEADER} has no version parameter")
    version = member.params["version"]
    if not isinstance(version, Decimal):  # an Integer is not a Decimal: 1 is not 1.0
        raise ProfileHeaderError(
            ResultCode.PARAMETER_VALUE_SYNTAX_ERROR, f"The version of {HEADER} is not a decimal such as 1.0")
    return str(member.value), version


def format_profile(profile: RppProfile) -> str:
    """The value of the response header: the profile applied."""
    member = http_sfv.Item(http_sfv.Token(profile.name))
    member.params["version"] = Decimal(profile.version)
    dictionary = http_sfv.Dictionary()
    dictionary["profile"] = member
    return str(dictionary)


def vary_with_profile(existing: str | None) -> str:
    """A `Vary` value that holds `RPP-Profile` besides what `existing` lists (RFC 9110 §12.5.5): the response depends on
    the profile the request names."""
    names = [name.strip() for name in (existing or "").split(",") if name.strip()]
    if "*" in names or any(name.lower() == HEADER.lower() for name in names):
        return ", ".join(names)
    return ", ".join([*names, HEADER])


_PROFILE_PARAMETER = re.compile(r"^profile(?:-version)?$", re.IGNORECASE)
_RPP_MEDIA_TYPE = re.compile(r"^application/rpp\+", re.IGNORECASE)


def _split(value: str, separator: str) -> list[str]:
    """The parts of `value` at a separator outside quoted strings."""
    parts, start, quoted, escaped = [], 0, False, False
    for index, char in enumerate(value):
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == separator:
            parts.append(value[start:index])
            start = index + 1
    return [*parts, value[start:]]


def has_profile_parameters(media_types: list[str]) -> bool:
    """Whether an Accept or Content-Type value carries the media type parameters of core §14.3 on an RPP media range
    (`application/rpp+*`): another media type may use a `profile` parameter of its own (RFC 6906)."""
    for value in media_types:
        for media_range in _split(value, ","):
            kind, *parameters = _split(media_range, ";")
            if not _RPP_MEDIA_TYPE.match(kind.strip()):
                continue
            if any(_PROFILE_PARAMETER.match(parameter.partition("=")[0].strip()) for parameter in parameters):
                return True
    return False
