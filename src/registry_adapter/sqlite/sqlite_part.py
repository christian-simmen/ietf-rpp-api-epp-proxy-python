from dataclasses import dataclass

from sqlalchemy import MetaData


@dataclass(frozen=True)
class SqlitePart:
    """The tables of one part of the database, the common one or that of an extension, in a metadata of their own, with
    the version of their schema. The database keeps the version of each part it created."""
    name: str
    version: int
    metadata: MetaData
