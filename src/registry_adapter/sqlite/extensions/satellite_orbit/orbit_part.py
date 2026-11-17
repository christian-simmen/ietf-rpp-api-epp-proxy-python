from registry_adapter.sqlite.extensions.satellite_orbit.models.base import Base
from registry_adapter.sqlite.extensions.satellite_orbit.models.orbit_row import OrbitRow  # noqa: F401 - in the metadata
from registry_adapter.sqlite.sqlite_part import SqlitePart

PART = SqlitePart(name="satellite_orbit", version=1, metadata=Base.metadata)
