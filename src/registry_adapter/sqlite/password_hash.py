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


# What a login with an unknown user is compared with, so that it takes as long as a known one's.
UNKNOWN_USER_HASH = hash_password("no-such-client", n=2 ** 10)
