from connexion.security import BearerSecurityHandler


class BearerRefusingSecurityHandler(BearerSecurityHandler):
    """
    HTTP Bearer handler of a proxy that authenticates by HTTP Basic only. The spec offers `BearerAuth`; the scheme is
    skipped, as Connexion skips a scheme without a function, but without its warning once per operation (#189). A
    request with a Bearer token is then unauthenticated: 401.
    """

    def get_fn(self, security_scheme, required_scopes):
        return None
