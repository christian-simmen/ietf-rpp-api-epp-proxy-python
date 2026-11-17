from registry_adapter.sqlite.extensions.planet_atmosphere.models.atmosphere_row import AtmosphereRow  # noqa: F401 - in the metadata
from registry_adapter.sqlite.extensions.planet_atmosphere.models.base import Base
from registry_adapter.sqlite.sqlite_part import SqlitePart

PART = SqlitePart(name="planet_atmosphere", version=1, metadata=Base.metadata)
