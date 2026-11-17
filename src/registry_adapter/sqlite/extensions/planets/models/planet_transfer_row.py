from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from registry_adapter.sqlite.extensions.planets.models.base import Base


class PlanetTransferRow(Base):
    """The latest transfer of a planet, which is pending until the sponsor answers it or the requester cancels it."""
    __tablename__ = "planet_transfers"

    planet_id: Mapped[str] = mapped_column(String, ForeignKey("planets.id", ondelete="CASCADE"), primary_key=True)
    status: Mapped[str] = mapped_column(String)
    requesting_client: Mapped[str] = mapped_column(String)
    request_date: Mapped[str] = mapped_column(String)
    acting_client: Mapped[str] = mapped_column(String)
    action_date: Mapped[str] = mapped_column(String)
