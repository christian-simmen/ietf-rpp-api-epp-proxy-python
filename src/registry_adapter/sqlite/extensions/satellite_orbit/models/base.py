from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """The base of the models of the satellite orbit part: its tables are in this metadata only."""
    metadata = MetaData()
