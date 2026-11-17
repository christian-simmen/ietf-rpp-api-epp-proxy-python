from extensions.planets.core.model.satellite_changes import SatelliteChanges
from extensions.planets.rpp.mapping.object_members import SATELLITE_MEMBERS
from rpp.dto.rpp_patch_operation import RPPPatchOperation
from rpp.mapping.shared.common import parse_rpp
from rpp.schema.validator import refuse_removal_by_profile, validate_request_schema

TYPE = "@type"

CHANGEABLE = ("orbitalPeriod",)


def _member(operation: RPPPatchOperation, extensions) -> str:
    if operation.op not in ("add", "remove", "replace"):
        raise ValueError(f"Operation '{operation.op}' is not allowed")
    if operation.match is not None:
        raise ValueError("'match' selects an element of an array, and no member of a satellite is one")
    member = operation.path[1:] if operation.path.startswith("/") else operation.path
    if member not in (*CHANGEABLE, *SATELLITE_MEMBERS.members(extensions)):
        raise ValueError(f"Path '{operation.path}' cannot be changed")
    return member


def rpp_to_model(rpp: list, extensions: tuple[str, ...] = ()) -> SatelliteChanges:
    """Translates a partial update (json §5.2) into the changes it asks for, as `planet_patch` does. The orbital period and
    the members of the extensions of the preset can change, the latter as a whole."""
    values: dict = {}
    cleared: set[str] = set()
    for operation in (parse_rpp(RPPPatchOperation, item) for item in rpp):
        member = _member(operation, extensions)
        if operation.op == "remove":
            refuse_removal_by_profile("satellite.update", member, extensions)
            values.pop(member, None)
            cleared.add(member)
            continue
        if operation.value is None:
            raise ValueError(f"'{operation.op}' needs a 'value'")
        validate_request_schema("satellite.update", {TYPE: "satellite", member: operation.value}, extensions, member=member)
        values[member] = operation.value
        cleared.discard(member)
    return SatelliteChanges(
        orbitalPeriod=values.get("orbitalPeriod"), cleared=frozenset(cleared & {"orbitalPeriod"}),
        extensions=SATELLITE_MEMBERS.changes(values, cleared, extensions))
