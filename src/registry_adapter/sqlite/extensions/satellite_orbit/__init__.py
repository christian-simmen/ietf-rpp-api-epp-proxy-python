from registry_adapter.sqlite.extensions.satellite_orbit.orbit_hook import OrbitHook
from registry_adapter.sqlite.extensions.satellite_orbit.orbit_part import PART

HOOKS = {"satellite": OrbitHook()}

__all__ = ["HOOKS", "PART"]
