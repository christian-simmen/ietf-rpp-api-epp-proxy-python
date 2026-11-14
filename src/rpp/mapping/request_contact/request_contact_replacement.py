from core.model.request_contact.request_contact import RequestContact
from rpp.dto.rpp_request_contact_update import RPPRequestContactUpdate
from rpp.mapping.shared.common import parse_rpp
from rpp.schema.validator import validate_schema

TYPE = "@type"

CHANGEABLE = ("uriTemplate",)


def rpp_to_model(contact_id: str, rpp: dict) -> RequestContact:
    """Converts a full update to the request contact it asks for. A member outside `requestContact.update` is
    rejected, also a create-only or a read-only one (json §4.4, core §16.8)."""
    validate_schema("requestContact.update", rpp)
    for member in sorted(rpp.keys() - {TYPE, *CHANGEABLE}):
        raise ValueError(f"'{member}' cannot be sent in a full update")
    update = parse_rpp(RPPRequestContactUpdate, rpp)
    return RequestContact(id=contact_id, uriTemplate=update.uriTemplate)
