"""Request contacts over the wire of the app composed for RRI: the paths `/requestContacts` the rri extension adds
(docs/rri/rri-extension.md), and the request contacts of a domain."""
import base64

import pytest

from core.session.session_pool import SessionPool
from rpp.http.app import create_app
from tests.helper.fake_epp_client import FakeEppClient
from tests.helper.fake_rri_client import error, reply
from tests.helper.epp_backends import epp_backends
from tests.helper.profiles import EPP_PROFILE
from tests.unit.test_rri_adapter import CONTACT_INFO, DOMAIN_INFO, NAME
from tests.unit.test_rri_request_contacts import HANDLE, REQUEST_INFO, TEMPLATE
from tests.unit.test_rri_wire import BODY_HEADERS, HEADERS, MEDIA_TYPE, setup

URL = f"/requestContacts/{HANDLE}"

OTHER = "mailto:abuse@example.com"

CHECK_FREE = reply(data=('<contact:checkData xmlns:contact="http://registry.denic.de/contact/5.0">'
                         f'<contact:handle>{HANDLE}</contact:handle><contact:status>free</contact:status>'
                         '</contact:checkData>'))

PATCH_HEADERS = BODY_HEADERS


def assert_request_contact(body, template=TEMPLATE):
    assert body == {"@type": "requestContact", "id": HANDLE, "uriTemplate": template,
                    "provMetadata": {"@type": "provMetadata", "spClientId": "DENIC-1000022",
                                     "upDate": "2026-11-12T00:20:20.000000Z"}}


def test_create_answers_the_request_contact_read_back():
    client, clients = setup(reply(), REQUEST_INFO)

    response = client.post("/requestContacts", json={"@type": "requestContact", "id": HANDLE, "uriTemplate": TEMPLATE},
                           headers=BODY_HEADERS)

    assert response.status_code == 201, response.text
    assert response.headers["Location"].endswith(URL)
    assert_request_contact(response.json())
    assert "<contact:type>REQUEST</contact:type>" in clients[0].sent[0]


def test_create_of_a_contact_body_sends_nothing():
    client, clients = setup()

    response = client.post("/requestContacts", json={"@type": "contact", "id": HANDLE, "uriTemplate": TEMPLATE},
                           headers=BODY_HEADERS)

    assert response.status_code == 400, response.text
    assert all(not c.sent for c in clients)


def test_a_template_the_registry_refuses_is_a_bad_request():
    client, _ = setup(error("83000000005", "Validation of URI-Template failed"))

    response = client.post("/requestContacts", json={"@type": "requestContact", "id": HANDLE,
                                                     "uriTemplate": "ftp://example.com/"}, headers=BODY_HEADERS)

    assert response.status_code == 400, response.text
    assert response.headers["RPP-Code"] == "02005"


def test_read():
    client, _ = setup(REQUEST_INFO)

    response = client.get(URL, headers=HEADERS)

    assert response.status_code == 200, response.text
    assert_request_contact(response.json())


def test_a_person_is_no_request_contact():
    client, _ = setup(CONTACT_INFO)

    response = client.get("/requestContacts/DENIC-1000022-HOLDER", headers=HEADERS)

    assert response.status_code == 404 and response.headers["RPP-Code"] == "02303"


def test_a_request_contact_is_no_contact():
    client, _ = setup(REQUEST_INFO)

    response = client.get(f"/contacts/{HANDLE}", headers=HEADERS)

    assert response.status_code == 404 and response.headers["RPP-Code"] == "02303"


def test_full_update():
    client, clients = setup(REQUEST_INFO, reply(), REQUEST_INFO)

    response = client.put(URL, json={"@type": "requestContact", "uriTemplate": OTHER}, headers=BODY_HEADERS)

    assert response.status_code == 200, response.text
    assert f"<contact:uri-template>{OTHER}</contact:uri-template>" in clients[0].sent[1]


def test_partial_update():
    client, clients = setup(REQUEST_INFO, reply(), REQUEST_INFO)

    response = client.patch(URL, json=[{"op": "replace", "path": "/uriTemplate", "value": OTHER}],
                            headers=PATCH_HEADERS)

    assert response.status_code == 200, response.text
    assert f"<contact:uri-template>{OTHER}</contact:uri-template>" in clients[0].sent[1]


def test_delete_is_not_implemented():
    client, clients = setup()

    response = client.delete(URL, headers=HEADERS)

    assert response.status_code == 501 and response.headers["RPP-Code"] == "02101"
    assert all(not c.sent for c in clients)


def test_availability():
    client, _ = setup(CHECK_FREE)

    response = client.get(f"{URL}/availability", headers=HEADERS)

    assert response.status_code == 200, response.text
    assert response.json() == {"@type": "requestContactAvailability", "available": True}


def test_availability_head():
    client, _ = setup(CHECK_FREE)

    assert client.head(f"{URL}/availability", headers=HEADERS).status_code == 200


def test_include_elements_names_no_element_of_a_request_contact():
    client, clients = setup()

    response = client.get(URL, params={"includeElements": "authInfo"}, headers=HEADERS)

    assert response.status_code == 400, response.text
    assert all(not c.sent for c in clients)


def test_a_domain_shows_its_request_contacts_as_members():
    client, _ = setup(DOMAIN_INFO)

    body = client.get(f"/domainNames/{NAME}", headers=HEADERS).json()

    assert body["generalRequest"] == {"@type": "requestContact", "id": "DENIC-1000022-GENREQ"}
    assert body["abuse"] == {"@type": "requestContact", "id": "DENIC-1000022-GENREQ"}
    assert "contacts" not in body


def test_a_domain_create_sends_the_request_contacts_in_their_roles():
    client, clients = setup(reply(), DOMAIN_INFO)

    response = client.post("/domainNames", json={
        "@type": "domainName", "name": NAME, "registrant": {"@type": "contact", "id": "DENIC-1000022-HOLDER"},
        "generalRequest": {"@type": "requestContact", "id": "DENIC-1000022-GR"},
        "abuse": {"@type": "requestContact", "id": "DENIC-1000022-AB"},
        "dns": {"@type": "dnsData", "records": [{"@type": "dnsRecord", "name": "@", "type": "a",
                                                 "rdata": {"address": "192.0.2.10"}}]}}, headers=BODY_HEADERS)

    assert response.status_code == 201, response.text
    assert '<domain:contact role="generalrequest">DENIC-1000022-GR</domain:contact>' in clients[0].sent[0]
    assert '<domain:contact role="abusecontact">DENIC-1000022-AB</domain:contact>' in clients[0].sent[0]


@pytest.mark.parametrize("method, url", [("GET", URL), ("POST", "/requestContacts"), ("GET", f"{URL}/availability")])
def test_epp_has_no_request_contact_paths(method, url):
    app = create_app(SessionPool(epp_backends(lambda u, p: FakeEppClient(u, p))), EPP_PROFILE)
    headers = {"Authorization": "Basic " + base64.b64encode(b"ClientX:pw").decode(), "Accept": MEDIA_TYPE}

    response = app.test_client().request(method, url, headers=headers)

    assert response.status_code == 404, response.text


def test_a_domain_patch_removes_a_request_contact():
    client, clients = setup(DOMAIN_INFO, reply(), DOMAIN_INFO)

    response = client.patch(f"/domainNames/{NAME}", json=[{"op": "remove", "path": "/abuse"}], headers=BODY_HEADERS)

    assert response.status_code == 200, response.text
    update = clients[0].sent[1]
    assert "<domain:update>" in update and 'role="abusecontact"' not in update
    assert '<domain:contact role="generalrequest">DENIC-1000022-GENREQ</domain:contact>' in update


def test_a_domain_label_of_a_request_role_is_refused():
    client, clients = setup()

    response = client.patch(f"/domainNames/{NAME}", json=[{"op": "add", "path": "/contacts", "value": {
        "label": "abuse", "object": {"@type": "contact", "id": "DENIC-1000022-AB"}}}], headers=BODY_HEADERS)

    assert response.status_code == 501 and response.headers["RPP-Code"] == "02102"
    assert all(not c.sent for c in clients)
