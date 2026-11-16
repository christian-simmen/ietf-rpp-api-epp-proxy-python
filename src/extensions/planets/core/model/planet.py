from dataclasses import dataclass
from typing import Optional

from core.model.shared.common import ProvisioningObject

PLANET_TYPES = ("rocky", "gas-giant", "ice-giant")


@dataclass(kw_only=True)
class Planet(ProvisioningObject):
    """A planet of the demo extension `org.example.rpp.extension.planets` (docs/demo/planets-extension.md).

    `satellites` are the ids of its satellites, `pending_transfer` whether a transfer of it waits for an answer.
    """
    id: str
    type: str
    radius: Optional[float] = None
    mass: Optional[float] = None
    satellites: tuple[str, ...] = ()
    pending_transfer: bool = False
