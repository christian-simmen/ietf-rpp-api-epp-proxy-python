"""The request contacts of a domain (docs/rri/rri-extension.md): `generalRequest` and `abuse`, members the rri
extension adds to a domain, each a reference to a request contact. The model holds them as contact references whose
role is the member's name."""
import pytest
from jsonschema import ValidationError

from core.capabilities.not_supported_by_backend import NotSupportedByBackend
from core.model.contact.contacts import ContactMinimal
from core.model.domain.domains import ContactReference, ContactReferenceNew, Domain
from rpp.mapping.domain import domain_patch, domain_replacement, domains
from rpp.mapping.shared.patch_not_applicable import PatchNotApplicable
from tests.helper.profiles import EPP_PROFILE, RRI_PROFILE

# the tests map without an app, so a validator is built on first use (tests/conftest.py)
pytestmark = pytest.mark.lazy_schemas

NAME = "example.de"

HOLDER = {"@type": "contact", "id": "DENIC-1000022-HOLDER"}

GR = {"@type": "requestContact", "id": "DENIC-1000022-GR"}

AB = {"@type": "requestContact", "id": "DENIC-1000022-AB"}

DNS = {"@type": "dnsData", "records": [
    {"@type": "dnsRecord", "name": "@", "type": "a", "rdata": {"address": "192.0.2.10"}}]}

CREATE = {"@type": "domainName", "name": NAME, "registrant": HOLDER, "dns": DNS}

STORED = Domain(name=NAME, status=["ok"], clID="DENIC-1000022", contacts=[
    ContactReference(id="DENIC-1000022-HOLDER", types=["registrant"]),
    ContactReference(id="DENIC-1000022-GR", types=["generalRequest"]),
    ContactReference(id="DENIC-1000022-AB", types=["abuse"]),
])

EXTENSIONS = RRI_PROFILE.extensions


def roles(contacts):
    return [(c.type, c.contact.id) for c in contacts]


def test_a_create_takes_the_request_contacts_as_roles():
    domain = domains.rpp_to_model({**CREATE, "generalRequest": GR, "abuse": AB}, profile=RRI_PROFILE)

    assert domain.contacts == [ContactReference(id="DENIC-1000022-HOLDER", types=["registrant"]),
                               ContactReference(id="DENIC-1000022-GR", types=["generalRequest"]),
                               ContactReference(id="DENIC-1000022-AB", types=["abuse"])]


def test_without_the_extension_the_request_contacts_are_undeclared():
    with pytest.raises(ValueError, match="Undeclared"):
        domains.rpp_to_model({**CREATE, "generalRequest": GR}, profile=EPP_PROFILE)


def test_a_request_contact_is_no_contact_of_the_domain():
    with pytest.raises(ValidationError, match="requestContact"):
        domains.rpp_to_model({**CREATE, "abuse": HOLDER}, profile=RRI_PROFILE)


@pytest.mark.parametrize("label", ["generalRequest", "abuse"])
def test_the_roles_are_no_contact_labels(label):
    contacts = [{"label": label, "object": HOLDER}]

    with pytest.raises(NotSupportedByBackend, match=label):
        domains.rpp_to_model({**CREATE, "contacts": contacts}, profile=RRI_PROFILE)


def test_a_read_shows_the_request_contacts_as_members():
    domain = domains.model_to_rpp(STORED, extensions=EXTENSIONS)

    assert domain["generalRequest"] == GR and domain["abuse"] == AB
    assert "contacts" not in domain
    assert domain["registrant"] == HOLDER


def test_a_further_holder_stays_a_contact():
    stored = Domain(name=NAME, status=["ok"], clID="DENIC-1000022", contacts=[
        *STORED.contacts, ContactReference(id="DENIC-1000022-H2", types=["registrant"])])

    domain = domains.model_to_rpp(stored, extensions=EXTENSIONS)

    assert domain["contacts"] == [{"label": "registrant", "object": {"@type": "contact", "id": "DENIC-1000022-H2"}}]


def test_a_full_update_states_the_request_contacts():
    wanted = domain_replacement.rpp_to_model(
        NAME, {"@type": "domainName", "registrant": HOLDER, "dns": DNS, "generalRequest": GR}, profile=RRI_PROFILE)

    assert roles(wanted.contacts) == [("generalRequest", "DENIC-1000022-GR")]


def test_a_full_update_without_them_clears_them():
    wanted = domain_replacement.rpp_to_model(
        NAME, {"@type": "domainName", "registrant": HOLDER, "dns": DNS}, profile=RRI_PROFILE)

    assert wanted.contacts == []


def test_a_full_update_without_the_extension_cannot_send_them():
    with pytest.raises(ValueError):
        domain_replacement.rpp_to_model(NAME, {"@type": "domainName", "generalRequest": GR}, profile=EPP_PROFILE)


@pytest.mark.parametrize("operation", [
    {"op": "replace", "path": "/abuse", "value": GR},
    {"op": "add", "path": "/generalRequest", "value": GR},
    {"op": "remove", "path": "/abuse"},
])
def test_a_patch_of_a_request_contact_reads_the_domain(operation):
    assert domain_patch.rpp_to_model(NAME, [operation], profile=RRI_PROFILE) is None


def test_a_patch_of_a_request_contact_without_the_extension_is_refused():
    with pytest.raises(ValueError, match="/abuse"):
        domain_patch.rpp_to_model(NAME, [{"op": "remove", "path": "/abuse"}], profile=EPP_PROFILE)


def test_a_patch_replaces_a_request_contact():
    current = domains.model_to_rpp(STORED, extensions=EXTENSIONS)

    wanted = domain_patch.rpp_to_model_with_current(
        NAME, [{"op": "replace", "path": "/abuse", "value": GR}], current, profile=RRI_PROFILE)

    assert roles(wanted.contacts) == [("generalRequest", "DENIC-1000022-GR"), ("abuse", "DENIC-1000022-GR")]


def test_a_patch_removes_a_request_contact():
    current = domains.model_to_rpp(STORED, extensions=EXTENSIONS)

    wanted = domain_patch.rpp_to_model_with_current(
        NAME, [{"op": "remove", "path": "/generalRequest"}], current, profile=RRI_PROFILE)

    assert wanted.contacts == [ContactReferenceNew(type="abuse", contact=ContactMinimal(id="DENIC-1000022-AB"))]


def test_a_patch_cannot_remove_a_request_contact_the_domain_has_not():
    current = domains.model_to_rpp(Domain(name=NAME, status=["ok"], clID="DENIC-1000022", contacts=STORED.contacts[:1]),
                                   extensions=EXTENSIONS)

    with pytest.raises(PatchNotApplicable, match="/abuse"):
        domain_patch.rpp_to_model_with_current(NAME, [{"op": "remove", "path": "/abuse"}], current, profile=RRI_PROFILE)
