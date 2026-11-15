"""What a URL must be to be a prefix the server publishes (the base URL of its discovery document, which the `$id` of a
profile's schema starts with)."""
import re
from urllib.parse import urlsplit

# The characters a URI may have (RFC 3986), without `?` and `#`, which the base URL may not have anyway.
_URI_CHARACTERS = re.compile(r"[A-Za-z0-9\-._~:/\[\]@!$&'()*+,;=%]+")


def text(value) -> bool:
    """A non-empty string with no control characters and no padding."""
    return isinstance(value, str) and bool(value) and value == value.strip() and not any(ord(c) < 32 or ord(c) == 127 for c in value)


def https_url(value) -> bool:
    """An absolute https URL with a host, usable as a prefix: no userinfo, query or fragment, and no malformed escape."""
    if not text(value) or not _URI_CHARACTERS.fullmatch(value) or any(c.isspace() or c == "\\" for c in value) or re.search(r"%(?![0-9A-Fa-f]{2})", value):
        return False
    try:
        parts = urlsplit(value)
        parts.port  # raises ValueError for a port that is not a number or out of range
        return (
            parts.scheme == "https" and bool(parts.hostname) and "@" not in parts.netloc
            and "?" not in value and "#" not in value
        )
    except ValueError:
        return False


