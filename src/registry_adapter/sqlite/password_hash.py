"""Password hashes of the clients of the SQLite demo backend: a self-describing string
`scrypt$<n>$<r>$<p>$<salt>$<hash>` (salt and hash in base64), made with `hashlib.scrypt` and compared in constant time.
A hash is a credential: nothing here logs a password or a hash."""
import base64
import hashlib
import hmac
import os

SCHEME = "scrypt"
N, R, P = 2 ** 14, 8, 1
KEY_LENGTH = 32
SALT_LENGTH = 16
# scrypt needs about 128 * n * r bytes
MAX_MEMORY = 128 * 1024 * 1024


def _scrypt(password: str, salt: bytes, n: int, r: int, p: int) -> bytes:
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=n, r=r, p=p, dklen=KEY_LENGTH, maxmem=MAX_MEMORY)


def hash_password(password: str, n: int = N, r: int = R, p: int = P) -> str:
    salt = os.urandom(SALT_LENGTH)
    key = _scrypt(password, salt, n, r, p)
    return "$".join((SCHEME, str(n), str(r), str(p), base64.b64encode(salt).decode("ascii"),
                     base64.b64encode(key).decode("ascii")))


def verify_password(password: str, stored: str) -> bool:
    """Whether the password is the one of the hash. A hash that is malformed verifies nothing."""
    try:
        scheme, n, r, p, salt, key = stored.split("$")
        if scheme != SCHEME:
            return False
        expected = base64.b64decode(key, validate=True)
        actual = _scrypt(password, base64.b64decode(salt, validate=True), int(n), int(r), int(p))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, expected)


def check_hash(stored: str) -> str | None:
    """Why a hash cannot be used, None where it can. The reason never holds the hash or a part of it."""
    parts = stored.split("$") if isinstance(stored, str) else []
    if len(parts) != 6 or parts[0] != SCHEME:
        return f"it is not a {SCHEME}$n$r$p$salt$hash string"
    try:
        n, r, p = (int(value) for value in parts[1:4])
    except ValueError:
        return "n, r and p are not integers"
    if n < 2 or n & (n - 1):
        return "n is not a power of two above 1"
    if r >= 1 and n >= 2 ** (16 * r):
        return "n is not below 2^(16r)"
    if r < 1 or p < 1:
        return "r and p are not positive"
    if 128 * n * r > MAX_MEMORY or r * p >= 2 ** 30:
        return "its parameters need more memory than the backend allows"
    try:
        base64.b64decode(parts[4], validate=True)
        base64.b64decode(parts[5], validate=True)
    except ValueError:
        return "the salt or the hash is not base64"
    return None


def parameters(stored: str) -> tuple[int, int, int] | None:
    """The scrypt parameters (n, r, p) a hash states, None for one that is malformed."""
    try:
        scheme, n, r, p, _salt, _key = stored.split("$")
        return (int(n), int(r), int(p)) if scheme == SCHEME else None
    except ValueError:
        return None
