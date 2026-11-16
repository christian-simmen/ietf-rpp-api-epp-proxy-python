from extensions.planets.core.model.satellite import Satellite
from extensions.planets.core.model.satellite_replacement import SatelliteReplacement
from extensions.planets.rpp.mapping import satellite_replacement, satellites
from rpp.dto.rpp_patch_operation import RPPPatchOperation
from rpp.mapping.shared import json_patch
from rpp.mapping.shared.common import parse_rpp

TYPE = "@type"

CHANGEABLE = ("orbitalPeriod",)

PATHS = tuple(f"/{member}" for member in CHANGEABLE)


def _check(operation: RPPPatchOperation):
    if operation.op not in ("add", "remove", "replace"):
        raise ValueError(f"Operation '{operation.op}' is not allowed")
    if operation.path not in PATHS:
        raise ValueError(f"Path '{operation.path}' cannot be changed")


def rpp_to_model_with_current(satellite_id: str, rpp: list, current: Satellite,
                              extensions: tuple[str, ...] = ()) -> SatelliteReplacement:
    """Applies the patch (json §5.2.2) to the representation of the current satellite, and returns the full update it
    asks for. Only the orbital period can change."""
    operations = [parse_rpp(RPPPatchOperation, operation) for operation in rpp]
    for operation in operations:
        _check(operation)
    patched = json_patch.apply(satellites.model_to_rpp(current, extensions), operations, array_paths=())
    update = {TYPE: "satellite", **{member: patched[member] for member in CHANGEABLE if member in patched}}
    return satellite_replacement.rpp_to_model(satellite_id, update, extensions)
