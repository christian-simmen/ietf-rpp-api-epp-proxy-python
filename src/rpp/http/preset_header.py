"""The `RPP-Preset` header field (core §Header Signalling): an RFC 9651 Dictionary with a `preset` member (a Token) that carries
a `version` parameter (a Decimal), and the media type parameters that mean the other signalling method.

Parsing is `http-sfv`'s, which implements RFC 9651. This module enforces what §14.2 adds. Other members and parameters
are ignored (gap: §14.2 does not say what a server does with them).
"""
import re
from decimal import Decimal

import http_sfv

from core.result.result_code import ResultCode
from rpp.http.media_range import split
from rpp.http.vary import vary_with
from rpp.schema.offered_preset import OfferedPreset

HEADER = "RPP-Preset"


class PresetHeaderError(ValueError):
    """The header is refused: `code` is the RPP client error code (core §12.4), the message goes in the detail."""

    def __init__(self, code: ResultCode, message: str):
        super().__init__(message)
        self.code = code


def parse(values: list[str]) -> tuple[str, Decimal] | None:
    """The preset identifier and version a request names, None when it has no `RPP-Preset` header."""
    if not values:
        return None
    # RFC 9651 §4.2: the field lines are combined with a comma into one Dictionary, where a repeated key is the last.
    # An empty line is an empty Dictionary, which http-sfv does not parse, and adds nothing.
    combined = ", ".join(value.strip(" \t") for value in values if value.strip(" \t"))
    if not combined:
        raise PresetHeaderError(ResultCode.REQUIRED_PARAMETER_MISSING, f"{HEADER} has no preset member")
    dictionary = http_sfv.Dictionary()
    try:
        dictionary.parse(combined.encode("ascii"))
    except (ValueError, UnicodeEncodeError):
        raise PresetHeaderError(
            ResultCode.PARAMETER_VALUE_SYNTAX_ERROR, f"{HEADER} is not a Structured Field Dictionary") from None
    member = dictionary.get("preset")
    if member is None:
        raise PresetHeaderError(ResultCode.REQUIRED_PARAMETER_MISSING, f"{HEADER} has no preset member")
    if not isinstance(member, http_sfv.Item) or not isinstance(member.value, http_sfv.Token):
        raise PresetHeaderError(ResultCode.PARAMETER_VALUE_SYNTAX_ERROR, f"The preset of {HEADER} is not a token")
    if "version" not in member.params:
        raise PresetHeaderError(
            ResultCode.REQUIRED_PARAMETER_MISSING, f"The preset of {HEADER} has no version parameter")
    version = member.params["version"]
    if not isinstance(version, Decimal):  # an Integer is not a Decimal: 1 is not 1.0
        raise PresetHeaderError(
            ResultCode.PARAMETER_VALUE_SYNTAX_ERROR, f"The version of {HEADER} is not a decimal such as 1.0")
    return str(member.value), version


def format_preset(preset: OfferedPreset) -> str:
    """The value of the response header: the preset applied."""
    member = http_sfv.Item(http_sfv.Token(preset.id))
    member.params["version"] = Decimal(preset.version)
    dictionary = http_sfv.Dictionary()
    dictionary["preset"] = member
    return str(dictionary)


def vary_with_preset(existing: str | None) -> str:
    """A `Vary` value that holds `RPP-Preset` besides what `existing` lists (RFC 9110 §12.5.5): the response depends on
    the preset the request names."""
    return vary_with(existing, HEADER)


_PRESET_PARAMETER = re.compile(r"^preset(?:-version)?$", re.IGNORECASE)
_RPP_MEDIA_TYPE = re.compile(r"^application/rpp\+", re.IGNORECASE)


def has_preset_parameters(media_types: list[str]) -> bool:
    """Whether an Accept or Content-Type value carries the media type parameters of core §Media Type Signalling on an RPP
    media range (`application/rpp+*`): another media type may use a `preset` parameter of its own."""
    for value in media_types:
        for media_range in split(value, ","):
            kind, *parameters = split(media_range, ";")
            if not _RPP_MEDIA_TYPE.match(kind.strip()):
                continue
            if any(_PRESET_PARAMETER.match(parameter.partition("=")[0].strip()) for parameter in parameters):
                return True
    return False
