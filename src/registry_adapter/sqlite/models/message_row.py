from typing import Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from registry_adapter.sqlite.models.base import Base


class MessageRow(Base):
    """A message of the queue of one client. The demo backend queues the events of a transfer."""
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    client: Mapped[str] = mapped_column(String, index=True)
    created: Mapped[str] = mapped_column(String)
    text: Mapped[str] = mapped_column(String)
    object_type: Mapped[str] = mapped_column(String)
    object_id: Mapped[str] = mapped_column(String)
    tr_status: Mapped[str] = mapped_column(String)
    request_date: Mapped[str] = mapped_column(String)
    action_date: Mapped[str] = mapped_column(String)
    requesting_client: Mapped[str] = mapped_column(String)
    acting_client: Mapped[str] = mapped_column(String)
    lang: Mapped[Optional[str]] = mapped_column(String, nullable=True)
