import sqlite3
import threading
import time
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from registry_adapter.sqlite.migrations import migrate
from registry_adapter.sqlite.sqlite_part import SqlitePart

# How long a unit of work waits for the write lock that another process holds, in seconds, before it fails.
BUSY_TIMEOUT_SECONDS = 30


class SqliteDatabase:
    """The database of the demo backend, a file or one in memory, with the tables of its parts created at start.

    A file can be shared by several processes, the workers of one instance (#184). Every unit of work begins IMMEDIATE,
    so it holds the write lock of the file from its first read: the units of work of all processes run one after the
    other, and none reads a value that another changes before it writes. pysqlite's own transaction handling is off,
    since it begins a transaction only at the first write and so lets a read before it go stale. A file is written
    ahead (WAL), and a unit of work waits BUSY_TIMEOUT_SECONDS for the lock. Within a process, one lock serialises the
    units of work as well: an in-memory database is one connection, shared by every thread.
    """

    def __init__(self, url: str, parts: list[SqlitePart]):
        parsed = make_url(url)
        if parsed.get_backend_name() != "sqlite":
            raise ValueError("rpp_sqlite_url must be a sqlite URL")
        in_memory = parsed.database in (None, "", ":memory:")
        options = {"connect_args": {"check_same_thread": False, "timeout": BUSY_TIMEOUT_SECONDS}}
        if in_memory:
            options["poolclass"] = StaticPool
        self.engine = create_engine(url, **options)

        @event.listens_for(self.engine, "connect")
        def _configure(connection, _record):
            connection.isolation_level = None
            if not in_memory:
                _write_ahead(connection)
            connection.execute("PRAGMA foreign_keys=ON")

        @event.listens_for(self.engine, "begin")
        def _begin_immediate(connection):
            connection.exec_driver_sql("BEGIN IMMEDIATE")

        migrate(self.engine, parts)
        self._lock = threading.RLock()

    @contextmanager
    def transaction(self):
        """One unit of work: a session that commits when the block ends, and rolls back when it fails."""
        with self._lock, Session(self.engine) as session, session.begin():
            yield session

    def close(self) -> None:
        self.engine.dispose()


def _write_ahead(connection: sqlite3.Connection) -> None:
    """Puts the file in WAL mode, which it keeps. The switch of a new file fails at once with "database is locked" while
    another process switches it, without the busy timeout, so it is tried again until the timeout has passed."""
    deadline = time.monotonic() + BUSY_TIMEOUT_SECONDS
    while True:
        try:
            connection.execute("PRAGMA journal_mode=WAL")
            return
        except sqlite3.OperationalError:
            if time.monotonic() >= deadline:
                raise
            time.sleep(0.05)
