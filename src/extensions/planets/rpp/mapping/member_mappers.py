from typing import Mapping

from extensions.planets.rpp.mapping.member_mapper import MemberMapper


class MemberMappers:
    """The mappers of the extensions that add members to one object (a planet or a satellite). Each extension adds its
    mapper when it registers, once (a second registration of the same id is no change, as for the schemas of the
    extensions), and the planets mappers use those of the extensions of the request's preset only: a member of another
    extension is undeclared, which the schema already refused (400)."""

    def __init__(self):
        self._by_id: dict[str, MemberMapper] = {}

    def add(self, mapper: MemberMapper) -> None:
        self._by_id.setdefault(mapper.extension_id, mapper)

    def of(self, extensions) -> list[MemberMapper]:
        return [mapper for extension_id, mapper in self._by_id.items() if extension_id in extensions]

    def members(self, extensions) -> tuple[str, ...]:
        """The names of the JSON members the extensions add."""
        return tuple(name for mapper in self.of(extensions) for name in mapper.members)

    def scope(self, extensions) -> frozenset[str]:
        """The extensions whose members a full update under these extensions replaces."""
        return frozenset(mapper.extension_id for mapper in self.of(extensions))

    def split(self, rpp: dict, extensions) -> tuple[dict, dict[str, object]]:
        """The members of the object that the planets extension defines, and the typed objects of the extensions' members."""
        rest = dict(rpp)
        typed: dict[str, object] = {}
        for mapper in self.of(extensions):
            present = {name: rest.pop(name) for name in mapper.members if name in rest}
            if present:
                typed[mapper.extension_id] = mapper.to_model(present)
        return rest, typed

    def changes(self, values: dict, cleared, extensions) -> dict[str, object]:
        """The typed changes of the extensions that a patch touches: the members it set and the members it removed."""
        typed: dict[str, object] = {}
        for mapper in self.of(extensions):
            own = {name: values[name] for name in mapper.members if name in values}
            removed = frozenset(name for name in mapper.members if name in cleared)
            if own or removed:
                typed[mapper.extension_id] = mapper.to_changes(own, removed)
        return typed

    def to_rpp(self, held: Mapping[str, object], extensions) -> dict:
        """The members of a read: those of the extensions of the response's preset, where the backend holds some."""
        rpp: dict = {}
        for mapper in self.of(extensions):
            if mapper.extension_id in held:
                rpp.update(mapper.to_rpp(held[mapper.extension_id]))
        return rpp
