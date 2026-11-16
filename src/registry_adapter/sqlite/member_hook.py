from typing import Protocol

from sqlalchemy.orm import Session


class MemberHook(Protocol):
    """What the SQLite part of an extension that adds members to an object of another extension does in the unit of work
    of that object's gateway. `value` and what `read` returns are typed objects of the adding extension's own core, never a
    JSON representation. A hook raises `MemberRefused` for a value that breaks its invariants, which rolls the unit back."""

    def create(self, session: Session, object_id: str, value: object) -> None: ...

    def replace(self, session: Session, object_id: str, value: object | None) -> None:
        """A full update: `None` removes the members."""

    def change(self, session: Session, object_id: str, changes: object) -> None:
        """A partial update: the members of `changes` are applied, the others stay."""

    def read(self, session: Session, object_id: str) -> object | None: ...

    def delete(self, session: Session, object_id: str) -> None: ...
