from registry_adapter.sqlite.password_hash import N, P, R, check_hash, hash_password, parameters, verify_password


class ClientDirectory:
    """The clients of the demo backend: each user and the hash of its password. The user is the sponsoring client."""

    def __init__(self, hashes: dict[str, str]):
        """A hash that cannot be used is a `ValueError` naming `rpp_sqlite_clients` and the user, never the hash."""
        for user, stored in hashes.items():
            reason = check_hash(stored)
            if reason is not None:
                raise ValueError(f"rpp_sqlite_clients: the hash of the client {user!r} cannot be used: {reason}")
        self._hashes = dict(hashes)
        # What a login of an unknown user is compared with: a hash with the parameters of the costliest configured one
        # (the largest n*r*p, the first on a tie), so that it costs what a known user's does and is never dearer than any
        # real hash. The default parameters where there are no clients.
        costliest = max((parameters(stored) for stored in self._hashes.values()),
                        key=lambda found: found[0] * found[1] * found[2], default=(N, R, P))
        self.stand_in_parameters = costliest
        self._stand_in = hash_password("no-such-client", *costliest)

    def verify(self, user: str, password: str) -> bool:
        stored = self._hashes.get(user)
        if stored is None:
            verify_password(password, self._stand_in)
            return False
        return verify_password(password, stored)
