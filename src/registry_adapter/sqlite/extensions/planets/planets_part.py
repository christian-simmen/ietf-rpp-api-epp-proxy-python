from registry_adapter.sqlite.extensions.planets.models.base import Base
from registry_adapter.sqlite.extensions.planets.models.planet_row import PlanetRow  # noqa: F401 - in the metadata
from registry_adapter.sqlite.extensions.planets.models.planet_transfer_row import PlanetTransferRow  # noqa: F401
from registry_adapter.sqlite.extensions.planets.models.satellite_row import SatelliteRow  # noqa: F401
from registry_adapter.sqlite.sqlite_part import SqlitePart

PART = SqlitePart(name="planets", version=1, metadata=Base.metadata)
