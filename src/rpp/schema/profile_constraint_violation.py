class ProfileConstraintViolation(Exception):
    """A request conforms to its preset and breaks a constraint of an applicable profile (json §Profiles and Validation,
    step 2): core §Extensions and Profiles of a Request has it refused with 02308 (422) and the `profile` of the error.
    `profile` is None where the failure cannot be attributed to one profile. The reason never holds a value of the request."""

    def __init__(self, profile: str | None, path: str, reason: str):
        super().__init__(reason)
        self.profile = profile
        self.path = path
        self.reason = reason
