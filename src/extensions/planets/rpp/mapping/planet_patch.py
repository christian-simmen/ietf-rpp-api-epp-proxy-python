from extensions.planets.core.model.planet_changes import PlanetChanges
from extensions.planets.rpp.dto.rpp_planet_update import RPPPlanetUpdate
from rpp.dto.rpp_patch_operation import RPPPatchOperation
from rpp.mapping.shared import auth_info
from rpp.mapping.shared.common import parse_rpp
from rpp.schema.validator import refuse_removal_by_profile, validate_request_schema

TYPE = "@type"

CHANGEABLE = ("type", "radius", "mass", "authInfo")

REMOVABLE = ("radius", "mass")

# A document that is valid for `planet.update` but for the member under test, which an operation's value replaces.
BASE = {TYPE: "planet", "type": "rocky"}


def _member(operation: RPPPatchOperation) -> str:
    if operation.op not in ("add", "remove", "replace"):
        raise ValueError(f"Operation '{operation.op}' is not allowed")
    if operation.match is not None:
        raise ValueError("'match' selects an element of an array, and no member of a planet is one")
    member = operation.path[1:] if operation.path.startswith("/") else operation.path
    if member not in CHANGEABLE:
        raise ValueError(f"Path '{operation.path}' cannot be changed")
    if operation.op == "remove" and member not in REMOVABLE:
        raise ValueError(f"'{member}' cannot be removed")
    return member


def rpp_to_model(rpp: list, extensions: tuple[str, ...] = ()) -> PlanetChanges:
    """Translates a partial update (json §5.2) into the changes it asks for, in order, the last on a member winning. The
    value of each operation is checked against the update schema. Nothing of the JSON Patch goes on: a `PlanetChanges`
    holds the members to set and those to remove. There is no object to validate, as there is no read (D24): the value of an
    operation is checked against the profiles as the member it sets, and the removal of a member a profile requires is
    refused; what a profile requires of the members together is not enforced."""
    values: dict = {}
    cleared: set[str] = set()
    for operation in (parse_rpp(RPPPatchOperation, item) for item in rpp):
        member = _member(operation)
        if operation.op == "remove":
            refuse_removal_by_profile("planet.update", member, extensions)
            values.pop(member, None)
            cleared.add(member)
            continue
        if operation.value is None:
            raise ValueError(f"'{operation.op}' needs a 'value'")
        validate_request_schema("planet.update", {**BASE, member: operation.value}, extensions, member=member)
        values[member] = operation.value
        cleared.discard(member)
    update = parse_rpp(RPPPlanetUpdate, {**BASE, **values}) if values else None
    return PlanetChanges(
        type=update.type if "type" in values else None, radius=update.radius if "radius" in values else None,
        mass=update.mass if "mass" in values else None,
        authInfo=auth_info.rpp_to_model(update.authInfo) if "authInfo" in values else None,
        cleared=frozenset(cleared))
