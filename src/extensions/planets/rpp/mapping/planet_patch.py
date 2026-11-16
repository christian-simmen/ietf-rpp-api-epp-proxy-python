from extensions.planets.core.model.planet import Planet
from extensions.planets.core.model.planet_replacement import PlanetReplacement
from extensions.planets.rpp.mapping import planet_replacement, planets
from rpp.dto.rpp_patch_operation import RPPPatchOperation
from rpp.mapping.shared import json_patch
from rpp.mapping.shared.common import parse_rpp

TYPE = "@type"

CHANGEABLE = ("type", "radius", "mass", "authInfo")

PATHS = tuple(f"/{member}" for member in CHANGEABLE)


def _check(operation: RPPPatchOperation):
    if operation.op not in ("add", "remove", "replace"):
        raise ValueError(f"Operation '{operation.op}' is not allowed")
    if operation.path not in PATHS:
        raise ValueError(f"Path '{operation.path}' cannot be changed")


def rpp_to_model_with_current(planet_id: str, rpp: list, current: Planet,
                              extensions: tuple[str, ...] = ()) -> PlanetReplacement:
    """Applies the patch (json §5.2.2) to the representation of the current planet, and returns the full update it asks
    for: what the patched planet holds of the members a client may change. A planet whose authInfo was not read (a
    client that is not the sponsor) has none, so the patch leaves its authInfo alone."""
    operations = [parse_rpp(RPPPatchOperation, operation) for operation in rpp]
    for operation in operations:
        _check(operation)
    patched = json_patch.apply(planets.model_to_rpp(current, frozenset(), extensions), operations, array_paths=())
    update = {TYPE: "planet", **{member: patched[member] for member in CHANGEABLE if member in patched}}
    return planet_replacement.rpp_to_model(planet_id, update, extensions)
