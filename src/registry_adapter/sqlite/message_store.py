from sqlalchemy import func, select
from sqlalchemy.orm import Session

from core.model.message.transfer_event import TransferEvent
from registry_adapter.sqlite.clock import now
from registry_adapter.sqlite.models.message_row import MessageRow


class MessageStore:
    """The message queues of the clients, which an extension's gateways write to, inside their own unit of work, and the
    message gateway reads."""

    @staticmethod
    def add_transfer_event(session: Session, client: str, event: TransferEvent, text: str, lang: str = "en") -> None:
        """Queues for `client` the message of a transfer: its event holds the process, which the message shows."""
        process = event.process
        session.add(MessageRow(
            client=client, created=now(), text=text, lang=lang, object_type=event.objectType, object_id=event.objectId,
            tr_status=event.trStatus, request_date=event.requestDate, action_date=event.actionDate,
            requesting_client=process.reqClientId, acting_client=process.actClientId))

    @staticmethod
    def head(session: Session, client: str) -> MessageRow | None:
        return session.scalars(select(MessageRow).where(MessageRow.client == client).order_by(MessageRow.id)).first()

    @staticmethod
    def size(session: Session, client: str) -> int:
        return session.scalar(select(func.count()).select_from(MessageRow).where(MessageRow.client == client)) or 0
