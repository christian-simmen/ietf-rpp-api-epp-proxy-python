from typing import Optional

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from registry_adapter.sqlite.extensions.planets.models.base import Base


class SatelliteRow(Base):
    """A satellite has no sponsor of its own: the sponsor of its planet is its sponsor, so it moves with the planet."""
    __tablename__ = "satellites"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    planet_id: Mapped[str] = mapped_column(String, ForeignKey("planets.id", ondelete="RESTRICT"), index=True)
    orbital_period: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    creator: Mapped[str] = mapped_column(String)
    created: Mapped[str] = mapped_column(String)
    updater: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    updated: Mapped[Optional[str]] = mapped_column(String, nullable=True)
