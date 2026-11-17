from typing import Optional

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from registry_adapter.sqlite.extensions.planet_atmosphere.models.base import Base


class AtmosphereRow(Base):
    """The atmosphere of a planet. There is no foreign key: the part of the planets extension is not this part's to import,
    and the hook of this extension removes the row in the unit of work that deletes the planet."""
    __tablename__ = "planet_atmospheres"

    planet_id: Mapped[str] = mapped_column(String, primary_key=True)
    pressure: Mapped[float] = mapped_column(Float)
    dominant_gas: Mapped[Optional[str]] = mapped_column(String, nullable=True)
