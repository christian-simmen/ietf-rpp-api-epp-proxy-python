from typing import Optional

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from registry_adapter.sqlite.extensions.satellite_orbit.models.base import Base


class OrbitRow(Base):
    """The orbit of a satellite. There is no foreign key: the part of the planets extension is not this part's to import, and
    the hook of this extension removes the row in the unit of work that deletes the satellite."""
    __tablename__ = "satellite_orbits"

    satellite_id: Mapped[str] = mapped_column(String, primary_key=True)
    semi_major_axis: Mapped[float] = mapped_column(Float)
    eccentricity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    inclination: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
