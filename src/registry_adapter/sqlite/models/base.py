from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """The base of the models of the common part: its tables are in this metadata only, as each part has its own."""
    metadata = MetaData()
