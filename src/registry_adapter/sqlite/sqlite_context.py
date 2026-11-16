from dataclasses import dataclass

from registry_adapter.sqlite.message_store import MessageStore
from registry_adapter.sqlite.sqlite_database import SqliteDatabase


@dataclass(frozen=True)
class SqliteContext:
    """What the gateways of one user's session work with: the database, the id of the client (the sponsor of what it
    creates) and the message queues."""
    database: SqliteDatabase
    sponsor_id: str
    messages: MessageStore
