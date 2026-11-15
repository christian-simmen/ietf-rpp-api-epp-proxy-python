"""The media ranges of `Accept` and the media type of `Content-Type` (RFC 9110 §8.3.1, §12.5.1), as far as core §14.3
reads them: the media type, the `q` weight, and the `profile` and `profile-version` parameters.

A parameter value is a token or a quoted-string (RFC 9110 §5.6.6), and both mean the same. A profile URN holds a colon,
which a token cannot, so a client quotes it.
"""
import re
from dataclasses import dataclass, field
from decimal import Decimal

from core.result.result_code import ResultCode
from rpp.http.media_range_error import MediaRangeError

PROFILE = "profile"
PROFILE_VERSION = "profile-version"

_TOKEN = re.compile(r"^[!#$%&'*+\-.^_`|~0-9A-Za-z]+$")
_QUALITY = re.compile(r"^(?:0(?:\.\d{0,3})?|1(?:\.0{0,3})?)$")
_VERSION = re.compile(r"^\d+\.\d+$")


@dataclass(frozen=True)
class MediaRange:
    """One media range or media type: `kind` is `type/subtype` in lower case, `parameters` the parameters in order with
    lower-case names (`q` and what follows it are not among them in an Accept range), `quality` the weight."""
    kind: str
    parameters: tuple[tuple[str, str], ...] = ()
    quality: Decimal = field(default=Decimal(1))

    def parameter(self, name: str) -> str | None:
        return next((value for key, value in self.parameters if key == name), None)

    def profile(self) -> tuple[str, Decimal] | None:
        """The profile name and version it names, None when it names none."""
        name, version = self.parameter(PROFILE), self.parameter(PROFILE_VERSION)
        if name is None and version is None:
            return None
        if name is None or version is None:
            raise MediaRangeError(
                ResultCode.REQUIRED_PARAMETER_MISSING,
                f"The media type parameters {PROFILE} and {PROFILE_VERSION} go together (core §12.4)")
        if not _VERSION.match(version):
            raise MediaRangeError(
                ResultCode.PARAMETER_VALUE_SYNTAX_ERROR, f"The {PROFILE_VERSION} is not a version such as 1.0")
        return name, Decimal(version)


def split(value: str, separator: str) -> list[str]:
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


def _syntax(message: str) -> MediaRangeError:
    return MediaRangeError(ResultCode.PARAMETER_VALUE_SYNTAX_ERROR, message)


def _value(text: str) -> str:
    """A parameter value: a token, or a quoted-string without its quotes and escapes."""
    if text.startswith('"'):
        if len(text) < 2 or not text.endswith('"'):
            raise _syntax("A quoted media type parameter is not closed")
        return re.sub(r"\\(.)", r"\1", text[1:-1])
    if not _TOKEN.match(text):
        raise _syntax("A media type parameter is neither a token nor a quoted string")
    return text


def _parse(text: str, weighted: bool) -> MediaRange:
    kind, *parts = split(text, ";")
    kind = kind.strip().lower()
    main, slash, sub = kind.partition("/")
    if not slash or not _TOKEN.match(main) or not _TOKEN.match(sub):
        raise _syntax("A media range is not type/subtype")
    parameters, quality = [], Decimal(1)
    for part in parts:
        if not part.strip():
            continue
        name, separator, value = part.partition("=")
        name = name.strip().lower()
        if not separator or not _TOKEN.match(name):
            raise _syntax("A media type parameter is not name=value")
        if weighted and name == "q":
            if not _QUALITY.match(value.strip()):
                raise _syntax("The q weight of a media range is a number from 0 to 1 with at most three decimals")
            quality = Decimal(value.strip())
            break  # RFC 9110 §12.5.1: what follows q is an extension of the Accept, not a media type parameter
        if name in (PROFILE, PROFILE_VERSION) and name in dict(parameters):
            raise _syntax(f"The media type parameter {name} is given twice")
        parameters.append((name, _value(value.strip())))
    return MediaRange(kind=kind, parameters=tuple(parameters), quality=quality)


def parse_accept(values: list[str]) -> list[MediaRange]:
    """The media ranges of the `Accept` field lines, in order."""
    return [_parse(item, weighted=True) for value in values for item in split(value, ",") if item.strip()]


def parse_media_type(value: str) -> MediaRange:
    """The media type of a `Content-Type` value."""
    return _parse(value, weighted=False)
