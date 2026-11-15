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
    if len(values) > 1:
        raise ProfileHeaderError(ResultCode.PARAMETER_VALUE_SYNTAX_ERROR, f"{HEADER} is given more than once")
    if not values[0].strip(" "):  # an empty Dictionary (RFC 9651 §4.2), which http-sfv does not parse
        raise ProfileHeaderError(ResultCode.REQUIRED_PARAMETER_MISSING, f"{HEADER} has no profile member")
    dictionary = http_sfv.Dictionary()
    try:
        dictionary.parse(values[0].encode("ascii"))
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


_QUOTED = re.compile(r'"(?:[^"\\]|\\.)*"')
_PROFILE_PARAMETER = re.compile(r";\s*profile(?:-version)?\s*=", re.IGNORECASE)


def has_profile_parameters(media_types: list[str]) -> bool:
    """Whether an Accept or Content-Type value carries the media type parameters of core §14.3."""
    return any(_PROFILE_PARAMETER.search(_QUOTED.sub('""', value)) for value in media_types)
