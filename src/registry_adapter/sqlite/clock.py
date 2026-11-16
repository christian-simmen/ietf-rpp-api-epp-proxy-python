import uuid
from datetime import datetime, timezone


def now() -> str:
    """The time of a change, as RPP shows dates (RFC 3339, UTC)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def new_server_transaction_id() -> str:
    return str(uuid.uuid4())
