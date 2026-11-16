import base64

import pytest

from core.session.session_pool import SessionPool
from tests.helper.profiles import EPP_PROFILE
from rpp.http.app import create_app
from tests.helper.contact_fixtures import card, put_body
from tests.helper.epp_backends import epp_backends
from tests.helper.fake_epp_client import FakeEppClient

CONTACT_NS = 'xmlns:contact="urn:ietf:params:xml:ns:contact-1.0"'

AUTH = {
    "Authorization": "Basic " + base64.b64encode(b"user:pw").decode(),
    "Accept": "application/rpp+json",
    "Content-Type": "application/rpp+json",
    "RPP-Cltrid": "cl-1",
}


def epp_reply(code, res_data=""):
    return (
        '<epp xmlns="urn:ietf:params:xml:ns:epp-1.0"><response>'
        f'<result code="{code}"><msg>Message</msg></result>{res_data}'
        '<trID><clTRID>cl-1</clTRID><svTRID>sv-1</svTRID></trID></response></epp>'
    )


def info(email="a@example.example", sponsor="user"):
    address = (
        '<contact:addr><contact:street>1 Main</contact:street><contact:city>Berlin</contact:city>'
        '<contact:sp>BE</contact:sp><contact:pc>10115</contact:pc><contact:cc>DE</contact:cc></contact:addr>'
    )
    return (True, "1000", epp_reply(1000, (
        f'<resData><contact:infData {CONTACT_NS}><contact:id>JD-1234</contact:id><contact:roid>C1</contact:roid>'
        f'<contact:status s="ok"/><contact:postalInfo type="int"><contact:name>John Doe</contact:name>{address}'
        f'</contact:postalInfo><contact:voice x="12">+49.123</contact:voice><contact:fax>+49.456</contact:fax>'
        f'<contact:email>{email}</contact:email><contact:clID>{sponsor}</contact:clID><contact:crID>user</contact:crID>'
        '<contact:crDate>2026-11-04T10:00:00.0Z</contact:crDate></contact:infData></resData>'
    )))


BASE_PRESET = "urn:ietf:params:rpp:preset:base"
DONE = (True, "1000", epp_reply(1000))
MISSING = (False, "2303", epp_reply(2303))
NEW_EMAIL = put_body(card(emails={"email": {"address": "b@example.example"}}))


class Session:
    def __init__(self, *replies):
        self.replies = replies
        self.client = None

    def _factory(self, username, password):
        self.client = FakeEppClient(username, password, replies=self.replies)
        return self.client

    def request(self, method, preset=None, **kwargs):
        http = create_app(SessionPool(epp_backends(self._factory)), EPP_PROFILE).test_client()
        headers = {**AUTH, "RPP-Preset": f"preset={preset};version=1.0"} if preset else AUTH
        return getattr(http, method)("/contacts/JD-1234", headers=headers, **kwargs)


def put(*replies, body=NEW_EMAIL):
    return Session(*replies).request("put", json=body)


def patch(*replies, body):
    return Session(*replies).request("patch", json=body)


def test_put_is_a_200_with_the_contact():
    response = put(info(), DONE, info("b@example.example"))

    assert response.status_code == 200
    assert response.headers["RPP-Code"] == "01000"
    assert response.json()["contactInfo"]["emails"] == {"email": {"address": "b@example.example"}}


def test_put_without_a_change_is_a_200_and_sends_no_update():
    session = Session(info())

    response = session.request("put", json=put_body())

    assert response.status_code == 200
    assert len(session.client.sent) == 1


def test_put_without_a_change_by_another_client_is_a_403():
    response = put(info(sponsor="other"), body=put_body())

    assert response.status_code == 403
    assert response.headers["RPP-Code"] == "02201"


def test_put_of_a_missing_contact_is_a_404():
    response = put(MISSING)

    assert response.status_code == 404 and response.headers["RPP-Code"] == "02303"


def test_put_whose_read_back_fails_is_a_202_without_a_body():
    response = put(info(), DONE, MISSING)

    assert response.status_code == 202
    assert response.text == ""
    assert response.headers["RPP-Code"] == "01000"


@pytest.mark.parametrize("body, status, code", [
    ({**NEW_EMAIL, "id": "JD-1234"}, 400, "02001"),
    (put_body(card(foo=1)), 400, "02001"),
    (put_body(disclose={"@type": "disclose"}), 501, "02102"),
    (put_body(authInfo={"@type": "authInfo", "method": "x", "authdata": "y"}), 400, "02001"),  # not included
])
def test_a_refused_put_sends_nothing_to_the_registry(body, status, code):
    session = Session(info())

    response = session.request("put", json=body)

    assert (response.status_code, response.headers["RPP-Code"]) == (status, code)
    assert session.client.sent == []


def test_patch_of_a_status_is_sent_without_a_read():
    session = Session(DONE, info())
    body = [{"op": "add", "path": "/status", "value": {"@type": "contactStatus", "label": "clientUpdateProhibited"}}]

    response = session.request("patch", preset=BASE_PRESET, json=body)      # the base preset has no profile to check

    assert response.status_code == 200
    assert "contact:update" in session.client.sent[0]


def test_patch_of_the_email_updates_without_a_read():
    session = Session(DONE, info("b@example.example"))

    response = session.request(
        "patch", preset=BASE_PRESET,
        json=[{"op": "replace", "path": "/contactInfo/emails/email/address", "value": "b@example.example"}],
    )

    assert response.status_code == 200
    assert response.json()["contactInfo"]["emails"]["email"]["address"] == "b@example.example"
    assert "<contact:email>b@example.example</contact:email>" in session.client.sent[0]


def test_patch_of_the_name_reads_and_updates():
    response = patch(info(), DONE, info(), body=[{"op": "replace", "path": "/contactInfo/name/full", "value": "Joe"}])

    assert response.status_code == 200


def test_patch_that_removes_the_organisation_that_is_not_there_is_a_422():
    response = patch(info(), body=[{"op": "remove", "path": "/contactInfo/organizations/org"}])

    assert response.status_code == 422 and response.headers["RPP-Code"] == "02308"


def test_patch_that_removes_the_name_is_a_422_under_the_epp_compatibility_profile():
    # the profile requires the name (draft-kowalik-rpp-epp-compatibility, profile.card); before presets this was the 501 of
    # the mapper, which a preset without the profile still answers
    response = patch(info(), body=[{"op": "remove", "path": "/contactInfo/name"}])

    assert response.status_code == 422 and response.headers["RPP-Code"] == "02308"
    assert response.json()["errors"][0]["profile"] == "urn:ietf:params:rpp:profile:epp-compatibility"


def test_put_adding_a_localization_the_registry_ignores_is_a_500_with_02400():
    body = put_body(card(localizations={"und": {"name": {"full": "Jörg"}}}))

    response = put(info(), DONE, info(), body=body)

    assert response.status_code == 500 and response.headers["RPP-Code"] == "02400"
    assert "loc" in response.json()["detail"]


def test_patch_without_a_read_under_the_epp_compatible_preset_is_checked_on_the_patched_contact():
    # replacing the email is one EPP value that needs no read, but the profile applies to every request (core): the contact
    # is read, patched, and the Profile Schema refuses a non-ASCII address
    session = Session(info())

    response = session.request(
        "patch", json=[{"op": "replace", "path": "/contactInfo/emails/email/address", "value": "jöhn@exämple.com"}])

    assert response.status_code == 422 and response.headers["RPP-Code"] == "02308"
    error = response.json()["errors"][0]
    assert error["profile"] == "urn:ietf:params:rpp:profile:epp-compatibility"
    assert error["paths"][0].startswith("$.contactInfo.emails")
    assert len(session.client.sent) == 1 and "contact:info" in session.client.sent[0]       # the read, no update
