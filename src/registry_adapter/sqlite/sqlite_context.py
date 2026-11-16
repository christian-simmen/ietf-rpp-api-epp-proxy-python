from dataclasses import dataclass, field
from typing import Mapping

from registry_adapter.sqlite.member_hook import MemberHook
from registry_adapter.sqlite.message_store import MessageStore
from registry_adapter.sqlite.sqlite_database import SqliteDatabase


@dataclass(frozen=True)
class SqliteContext:
    """What the gateways of one user's session work with: the database, the id of the client (the sponsor of what it
    creates), the message queues and the hooks of the extensions that add members."""
    database: SqliteDatabase
    sponsor_id: str
    messages: MessageStore
    # The hooks of the extensions that add members to an object, by the object (`planet`) and the extension id.
    hooks: Mapping[str, Mapping[str, MemberHook]] = field(default_factory=dict)
