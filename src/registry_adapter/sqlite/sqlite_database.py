import threading
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from registry_adapter.sqlite.migrations import migrate
from registry_adapter.sqlite.sqlite_part import SqlitePart


class SqliteDatabase:
    """The database of the demo backend, a file or one in memory, with the tables of its parts created at start.

    Every unit of work holds one lock: the demo is a test bed, not a server for load, and a single writer keeps SQLite
    (and an in-memory database, which is one connection) simple and correct.
    """

    def __init__(self, url: str, parts: list[SqlitePart]):
        parsed = make_url(url)
        if parsed.get_backend_name() != "sqlite":
            raise ValueError("rpp_sqlite_url must be a sqlite URL")
        in_memory = parsed.database in (None, "", ":memory:")
        options = {"connect_args": {"check_same_thread": False}}
        if in_memory:
            options["poolclass"] = StaticPool
        self.engine = create_engine(url, **options)

        @event.listens_for(self.engine, "connect")
        def _foreign_keys(connection, _record):
            connection.execute("PRAGMA foreign_keys=ON")

        migrate(self.engine, parts)
        self._lock = threading.RLock()

    @contextmanager
    def transaction(self):
        """One unit of work: a session that commits when the block ends, and rolls back when it fails."""
        with self._lock, Session(self.engine) as session, session.begin():
            yield session

    def close(self) -> None:
        self.engine.dispose()
