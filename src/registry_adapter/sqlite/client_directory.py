from registry_adapter.sqlite.password_hash import UNKNOWN_USER_HASH, verify_password


class ClientDirectory:
    """The clients of the demo backend: each user and the hash of its password. The user is the sponsoring client."""

    def __init__(self, hashes: dict[str, str]):
        self._hashes = dict(hashes)

    def verify(self, user: str, password: str) -> bool:
        stored = self._hashes.get(user)
        if stored is None:
            verify_password(password, UNKNOWN_USER_HASH)  # as long as a known user takes
            return False
        return verify_password(password, stored)
