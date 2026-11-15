from dataclasses import dataclass


@dataclass(kw_only=True)
class ProfileSchemaReference:
    """Where the effective schema of an offered profile is published."""
    profile: str
    version: str
    url: str
