"""The profiles over the wire: the Profile Data Object, discovery, the selected profile and what it allows."""
from dataclasses import replace

import pytest

from core.session.session_pool import SessionPool
from rpp.http.app import create_app
from rpp.http.header_profile_signalling import HeaderProfileSignalling
from rpp.http.profile_selection import ProfileSelection
from rpp.schema.profiles import PROFILES
from tests.helper.epp_backends import epp_backends
from tests.helper.fake_epp_client import FakeEppClient
from tests.helper.profiles import EPP_PROFILE, RRI_PROFILE
from tests.helper.fake_rri_client import FakeRriClient, rri_backends
from tests.unit.test_rri_wire import DISCOVERY, HEADERS, MEDIA_TYPE

BASE = "urn:ietf:params:rpp:profile:base"
EPP = "urn:ietf:params:rpp:profile:epp-compatibility"
RRI = "de.denic.rpp.profile.rri"
EPP_EXTENSION = "urn:ietf:params:rpp:extension:epp-compatibility"


def epp_client(profile=EPP_PROFILE):
    sessions = SessionPool(epp_backends(lambda username, password: FakeEppClient(username, password)))
    return create_app(sessions, profile, discovery_settings=DISCOVERY).test_client()


def rri_client(profile=RRI_PROFILE):
    sessions = SessionPool(rri_backends(lambda username, password: FakeRriClient(username, password, replies=[])))
    return create_app(sessions, profile, discovery_settings=DISCOVERY).test_client()


def read(client, name):
    return client.get(f"/profiles/{name}", headers=HEADERS)


def test_the_base_profile_is_read_with_its_objects_and_no_extension():
    response = read(epp_client(), BASE)

    assert response.status_code == 200
    assert response.headers["RPP-Code"] == "01000"
    assert response.json() == {
        "@type": "profile", "name": BASE, "version": "1.0", "rppVersion": "1.0", "defaultProfile": False,
        "description": "Base profile of the RPP proxy, the data objects of the RPP drafts without extensions",
        "objects": ["domainName", "contact", "host"],
    }


def test_the_epp_profile_is_the_default_and_has_the_constraint_extension_and_a_base():
    body = read(epp_client(), EPP).json()

    assert body["defaultProfile"] is True
    assert body["baseProfile"] == {"@type": "profile", "name": BASE}
    assert [(e["id"], e["version"]) for e in body["extensions"]] == [(EPP_EXTENSION, "1.0")]


def test_the_rri_profile_has_no_host_and_the_rri_extension():
    body = read(rri_client(), RRI).json()

    assert body["objects"] == ["domainName", "contact", "requestContact"]
    assert body["defaultProfile"] is True
    assert [e["id"] for e in body["extensions"]] == ["de.denic.rpp.rri"]


def test_a_profile_reads_the_same_on_every_server_even_where_the_backend_has_no_such_object():
    on_epp, on_rri = read(epp_client(), BASE).json(), read(rri_client(), BASE).json()

    assert on_epp == on_rri
    assert "host" in on_rri["objects"]


@pytest.mark.parametrize("client, name", [(epp_client(), RRI), (rri_client(), EPP), (epp_client(), "nope")])
def test_a_profile_the_server_does_not_offer_is_a_404(client, name):
    response = read(client, name)

    assert response.status_code == 404
    assert response.headers["RPP-Code"] == "02303"


def test_discovery_states_the_offered_profiles_and_their_extensions():
    epp = epp_client().get("/.well-known/rpp", headers=HEADERS).json()
    rri = rri_client().get("/.well-known/rpp", headers=HEADERS).json()

    assert epp["profiles"] == [BASE, EPP]
    assert [e["id"] for e in epp["extensions"]] == [EPP_EXTENSION]
    assert epp["objects"] == ["domainName", "host", "contact"]
    assert rri["profiles"] == [BASE, RRI]
    assert [e["id"] for e in rri["extensions"]] == ["de.denic.rpp.rri"]
    assert rri["objects"] == ["domainName", "contact", "requestContact"]


def test_the_default_profile_is_selected_and_an_object_outside_it_is_refused_before_any_command():
    response = rri_client().get("/hosts/ns1.example.de", headers=HEADERS)

    assert response.status_code == 501
    assert response.headers["RPP-Code"] == "02307"
    assert "rri" in response.json()["detail"]


def test_a_request_that_is_not_authenticated_is_a_401_not_a_hint_of_the_profiles():
    response = rri_client().get("/hosts/ns1.example.de", headers={"Accept": MEDIA_TYPE})

    assert response.status_code == 401


def test_a_path_no_operation_serves_stays_a_404_even_under_an_object_outside_the_profile():
    response = rri_client().get("/hosts/a/b/c/d", headers={"Accept": MEDIA_TYPE})

    assert response.status_code == 404


def test_an_object_the_backend_does_not_hold_is_refused_under_a_profile_that_lists_it():
    backend = RRI_PROFILE.with_changes({"profiles": ["base"], "default_profile": "base"})
    client = rri_client(backend)

    response = client.get("/hosts/ns1.example.de", headers=HEADERS)

    assert response.status_code == 501
    assert response.headers["RPP-Code"] == "02307"


def test_the_extension_paths_exist_for_the_extensions_of_an_offered_profile_only():
    assert epp_client().get("/requestContacts/X-1", headers=HEADERS).status_code == 404


@pytest.mark.parametrize("change, message", [
    ({"profiles": ["base", "nope"]}, "unknown RPP profile nope"),
    ({"profiles": ["base", "base"]}, "offered twice"),
    ({"default_profile": "rri"}, "not one of the offered"),
    ({"profiles": ["epp"], "default_profile": "epp"}, "base profile that is not offered"),
    ({"extensions": []}, "does not hold"),
])
def test_a_wrong_choice_of_profiles_stops_the_app(change, message):
    with pytest.raises(ValueError, match=message):
        create_app(None, EPP_PROFILE.with_changes(change))


def test_two_offered_profiles_with_one_name_stop_the_app(monkeypatch):
    monkeypatch.setitem(PROFILES, "epp", replace(PROFILES["epp"], name=BASE, base_profile=None))

    with pytest.raises(ValueError, match="the same name"):
        create_app(None, EPP_PROFILE)


class Selecting:
    """Stands for a signalling method of #163 or #164: the resolver is the one place a profile is chosen."""

    def __init__(self, monkeypatch, key):
        monkeypatch.setattr(HeaderProfileSignalling, "resolve", lambda self, scope: ProfileSelection.of(PROFILES[key]))


def test_a_selected_profile_decides_the_paths_the_extensions_and_nothing_else(monkeypatch):
    Selecting(monkeypatch, "base")
    client = rri_client()

    # The extension's object is outside base: refused before any command.
    refused = client.get("/requestContacts/DENIC-1000022-GR", headers=HEADERS)
    assert refused.status_code == 501 and refused.headers["RPP-Code"] == "02307"
    # An extension member is undeclared under base: the combined schema holds only the profile's extensions.
    body = {"@type": "domainName", "name": "foo.de", "generalRequest": {"@type": "requestContact", "id": "X-1"}}
    rejected = client.post("/domainNames", json=body, headers={**HEADERS, "Content-Type": MEDIA_TYPE})
    assert rejected.status_code == 400
