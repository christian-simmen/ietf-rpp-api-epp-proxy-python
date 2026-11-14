"""The request contacts of a domain: the members an offered extension adds to it that each refer to a request contact
(`generalRequest` and `abuse` of the rri extension, docs/rri/rri-extension.md). They are not `contacts`: the model
holds each as a contact reference whose role is the member's name, so a backend writes them as it writes a role."""
from rpp.schema.extensions import added_members

TYPE = "requestContact"

ROLES = ("generalRequest", "abuse")


def members(schema: str, extensions) -> tuple[str, ...]:
    """The request contact members the offered extensions add to a definition of the domain."""
    added = added_members(schema, extensions)
    return tuple(role for role in ROLES if role in added)


def split(rpp: dict, schema: str, extensions) -> tuple[dict, list[tuple[str, str]]]:
    """The representation without its request contacts, and the role and id of each it states."""
    names = members(schema, extensions)
    rest = {member: value for member, value in rpp.items() if member not in names}
    return rest, [(role, rpp[role]["id"]) for role in names if rpp.get(role)]


def to_rpp(roles: dict[str, str], extensions) -> dict:
    """The members of the request contacts a domain has, by role."""
    return {role: {"@type": TYPE, "id": roles[role]} for role in members("domainName.read", extensions)
            if role in roles}
