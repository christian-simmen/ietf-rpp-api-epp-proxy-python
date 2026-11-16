from sqlalchemy import Integer, MetaData, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class _VersionBase(DeclarativeBase):
    metadata = MetaData()


class SchemaVersionRow(_VersionBase):
    """The version of the schema of one part of the database, as the code that created it had it."""
    __tablename__ = "schema_versions"

    part: Mapped[str] = mapped_column(String, primary_key=True)
    version: Mapped[int] = mapped_column(Integer)
