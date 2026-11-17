from typing import Protocol


class MemberMapper(Protocol):
    """What an extension that adds members to a planet or a satellite gives the mappers of the planets extension: how its
    JSON members become the typed objects of its own core and back. Nothing of the JSON goes beyond the mapper, and the
    backend sees the typed objects only (`Planet.extensions`, `PlanetChanges.extensions`, `PlanetReplacement.extensions`)."""
    extension_id: str
    members: tuple[str, ...]

    def to_model(self, members: dict) -> object:
        """The members of a create or a full update that the request has (`members` holds those of `self.members`)."""

    def to_changes(self, values: dict, cleared: frozenset[str]) -> object:
        """The changes of a partial update: the members set (`values`, name to JSON value) and those removed."""

    def to_rpp(self, value: object) -> dict:
        """The members of a read, from what the backend holds."""
