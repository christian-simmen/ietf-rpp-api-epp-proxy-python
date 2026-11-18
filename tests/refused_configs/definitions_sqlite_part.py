"""The SQLite part of the test-only extensions: the backend holds an extension that has a part, and these have no tables."""
from sqlalchemy import MetaData

from registry_adapter.sqlite.sqlite_part import SqlitePart

PART = SqlitePart(name="refused_definitions", version=1, metadata=MetaData())
