from registry_adapter.sqlite.extensions.planet_atmosphere.atmosphere_hook import AtmosphereHook
from registry_adapter.sqlite.extensions.planet_atmosphere.atmosphere_part import PART

HOOKS = {"planet": AtmosphereHook()}

__all__ = ["HOOKS", "PART"]
