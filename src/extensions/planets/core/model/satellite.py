from dataclasses import dataclass
from typing import Optional

from core.model.shared.common import ProvisioningObject


@dataclass(kw_only=True)
class Satellite(ProvisioningObject):
    """A satellite of one planet (docs/demo/planets-extension.md). Its sponsor is the sponsor of its planet."""
    id: str
    planet: str
    orbitalPeriod: Optional[float] = None
