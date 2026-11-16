"""A PATCH is refused alike under a preset with profiles and under one without, and sends nothing (#178 review): the conversion
that needs no read runs first in both, so what it refuses is refused alike by construction, and only then the profile case
reads the object."""
import base64

import pytest

from core.session.session_pool import SessionPool
from rpp.http.app import create_app
from tests.helper.epp_backends import epp_backends
from tests.helper.fake_epp_client import FakeEppClient
from tests.helper.profiles import EPP_PROFILE
from tests.unit.test_rri_wire import DISCOVERY

MEDIA_TYPE = "application/rpp+json"
AUTH = {"Authorization": "Basic " + base64.b64encode(b"user:pw").decode(), "Accept": MEDIA_TYPE,
        "Content-Type": MEDIA_TYPE, "RPP-Cltrid": "cl-1"}
WITH_PROFILE = {**AUTH, "RPP-Preset": "preset=urn:ietf:params:rpp:preset:epp-compatible;version=1.0"}
WITHOUT = {**AUTH, "RPP-Preset": "preset=urn:ietf:params:rpp:preset:base;version=1.0"}


def patch(url, body, headers):
    clients = []

    def factory(username, password):
        clients.append(FakeEppClient(username, password))     # no reply: a command sent raises
        return clients[-1]

    http = create_app(SessionPool(epp_backends(factory)), EPP_PROFILE, discovery_settings=DISCOVERY).test_client()
    response = http.patch(url, json=body, headers=headers)
    return response, [message for client in clients for message in client.sent]


def op(kind, path, **rest):
    return {"op": kind, "path": path, **rest}


STATUS_ADD = op("add", "/status", value={"@type": "contactStatus", "label": "clientUpdateProhibited"})
CONTACT = "/contacts/JD-1234"
DOMAIN = "/domainNames/foo.example"

ROWS = [
    (CONTACT, [op("remove", "/authInfo")]),
    (CONTACT, [op("replace", "/authInfo", value={"pw": "x"})]),
    (CONTACT, [op("replace", "/foo", value=1)]),
    (CONTACT, [op("replace", "/disclose", value={})]),
    (CONTACT, [STATUS_ADD, op("replace", "/foo", value=1)]),              # a valid operation, then an invalid one
    (DOMAIN, [op("replace", "/authInfo", value={"pw": "x"})]),
    (DOMAIN, [op("replace", "/registrant", match={"id": "C-1"}, value={"@type": "contact", "id": "C-2"})]),
    (DOMAIN, [op("add", "/contacts", value={"label": "bogus", "object": {"@type": "contact", "id": "C-1"}})]),
    (DOMAIN, [op("replace", "/foo", value=1)]),
]


@pytest.mark.parametrize("url, body", ROWS, ids=[f"{u.split('/')[1]}-{i}" for i, (u, _) in enumerate(ROWS)])
def test_an_invalid_patch_gets_the_same_answer_under_both_presets_and_sends_nothing(url, body):
    with_profile, sent_with = patch(url, body, WITH_PROFILE)
    without, sent_without = patch(url, body, WITHOUT)

    assert with_profile.status_code == without.status_code and with_profile.status_code in (400, 501), with_profile.text
    assert with_profile.headers["RPP-Code"] == without.headers["RPP-Code"]
    assert with_profile.json()["detail"] == without.json()["detail"]
    assert sent_with == sent_without == []
