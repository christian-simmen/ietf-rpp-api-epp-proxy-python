from typing import Optional

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from registry_adapter.sqlite.extensions.planets.models.base import Base


class PlanetRow(Base):
    __tablename__ = "planets"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    type: Mapped[str] = mapped_column(String)
    radius: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mass: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    auth_pw: Mapped[str] = mapped_column(String)
    sponsor: Mapped[str] = mapped_column(String, index=True)
    creator: Mapped[str] = mapped_column(String)
    created: Mapped[str] = mapped_column(String)
    updater: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    updated: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    transferred: Mapped[Optional[str]] = mapped_column(String, nullable=True)
