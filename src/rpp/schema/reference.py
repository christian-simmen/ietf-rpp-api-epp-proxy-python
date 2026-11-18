from dataclasses import dataclass


@dataclass(frozen=True)
class Reference:
    """A reference to an extension, a profile or a preset by its identifier and exact version (data-objects R4)."""
    id: str
    version: str
