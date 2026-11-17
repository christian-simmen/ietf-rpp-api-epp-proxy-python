from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from registry_adapter.sqlite.schema_version_row import SchemaVersionRow
from registry_adapter.sqlite.sqlite_part import SqlitePart


def migrate(engine: Engine, parts: list[SqlitePart]) -> None:
    """Creates the tables of each part that the database does not have, and records its version. A part the database
    has at another version than the code is an error: there is no migration from one schema to another yet, so the
    database stays untouched and the app does not start."""
    SchemaVersionRow.metadata.create_all(engine)
    with Session(engine) as session:
        known = {row.part: row.version for row in session.scalars(select(SchemaVersionRow))}
    for part in parts:
        if part.name in known and known[part.name] != part.version:
            raise ValueError(
                f"The database has the part {part.name!r} at schema version {known[part.name]}, and the code needs "
                f"{part.version}")
    created = [part for part in parts if part.name not in known]
    for part in created:
        part.metadata.create_all(engine)
    with Session(engine) as session, session.begin():
        session.add_all(SchemaVersionRow(part=part.name, version=part.version) for part in created)
