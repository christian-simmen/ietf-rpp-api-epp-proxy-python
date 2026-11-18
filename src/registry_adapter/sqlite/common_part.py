from registry_adapter.sqlite.models.base import Base
from registry_adapter.sqlite.sqlite_part import SqlitePart

# The tables every deployment has: the message queue. The session and the clients are not in the database.
COMMON_PART = SqlitePart(name="common", version=1, metadata=Base.metadata)
