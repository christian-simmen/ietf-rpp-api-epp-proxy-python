import importlib
from dataclasses import dataclass, field
from typing import Callable, Mapping

from registry_adapter.sqlite.member_hook import MemberHook
from registry_adapter.sqlite.sqlite_context import SqliteContext
from registry_adapter.sqlite.sqlite_part import SqlitePart


@dataclass(frozen=True)
class ExtensionPart:
    """The SQLite part of an extension: its tables, the gateways it gives a session, and the hooks it adds to the objects
    of other extensions. The module of an extension (`registry_adapter.sqlite.extensions.<name>`) has `PART` (a
    `SqlitePart`), and `gateways(context)` where the extension has objects of its own, and `HOOKS` (`{object: MemberHook}`)
    where it adds members to those of another."""
    extension_id: str
    part: SqlitePart
    gateways: Callable[[SqliteContext], object] | None = None
    hooks: Mapping[str, MemberHook] = field(default_factory=dict)


def load_extension_parts(modules: dict[str, str]) -> list[ExtensionPart]:
    """Imports the module of each registered extension that the SQLite backend holds (by extension id)."""
    parts = []
    for extension_id, path in modules.items():
        try:
            module = importlib.import_module(path)
            parts.append(ExtensionPart(extension_id=extension_id, part=module.PART,
                                       gateways=getattr(module, "gateways", None), hooks=getattr(module, "HOOKS", {})))
        except (ImportError, AttributeError) as e:
            raise ValueError(f"The SQLite part {path!r} of the extension {extension_id} cannot be loaded: {e}") from e
    return parts
