"""Whether an `Accept` allows a value in its native media type (core §Native Media Types): the media type itself, a range that
includes it, or no `Accept` at all. The media ranges need not identify an RPP media type."""
from decimal import Decimal

from rpp.http import media_range


def _weight(ranges, target: str) -> Decimal:
    """The weight an `Accept` gives a media type: that of the most specific range that covers it (RFC 9110 §12.5.1), 0 where
    none does."""
    group = target.split("/")[0] + "/*"
    matching = [(3 if item.kind == target else 2 if item.kind == group else 1, item.quality)
                for item in ranges if item.kind in (target, group, "*/*")]
    return max(matching)[1] if matching else Decimal(0)


def accepts(accept_values: list[str], media_type: str) -> bool:
    """Absent `Accept` allows it, else the media type has a weight above 0. Parameters are ignored. Raises `MediaRangeError`
    for a value that does not parse."""
    ranges = media_range.parse_accept(accept_values)
    return not ranges or _weight(ranges, media_type) > 0
