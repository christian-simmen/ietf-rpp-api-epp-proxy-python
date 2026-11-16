from registry_adapter.sqlite.password_hash import N, P, R, hash_password, parameters, verify_password


class ClientDirectory:
    """The clients of the demo backend: each user and the hash of its password. The user is the sponsoring client."""

    def __init__(self, hashes: dict[str, str]):
        self._hashes = dict(hashes)
        # What a login of an unknown user is compared with: a hash of the strongest parameters of the configured ones, so
        # that it costs what a known user's does (the default parameters where none is configured).
        stated = [found for found in map(parameters, self._hashes.values()) if found is not None]
        self.stand_in_parameters = tuple(max(values) for values in zip(*stated)) if stated else (N, R, P)
        self._stand_in = hash_password("no-such-client", *self.stand_in_parameters)

    def verify(self, user: str, password: str) -> bool:
        stored = self._hashes.get(user)
        if stored is None:
            verify_password(password, self._stand_in)
            return False
        return verify_password(password, stored)
