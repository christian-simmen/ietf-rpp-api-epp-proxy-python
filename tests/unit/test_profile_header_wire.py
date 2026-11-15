"""Profile signalling with the RPP-Profile header (core §14.2): the selection, its refusals and the response header."""
import pytest

from rpp.http import profile_header
from rpp.schema.profiles import PROFILES
from tests.unit.test_profiles_wire import BASE, EPP, RRI, epp_client, rri_client
from tests.unit.test_rri_wire import HEADERS, MEDIA_TYPE

DISCOVERY = "/.well-known/rpp"


def named(profile, version="1.0", **extra):
    return {**HEADERS, "RPP-Profile": f"profile={profile};version={version}", **extra}


def applied(response):
    return response.headers.get("RPP-Profile")


def test_a_request_without_the_header_gets_the_default_profile_and_names_it():
    response = epp_client().get(DISCOVERY, headers=HEADERS)

    assert response.status_code == 200
    assert applied(response) == f"profile={EPP};version=1.0"


@pytest.mark.parametrize("name", [BASE, EPP])
def test_the_header_selects_an_offered_profile(name):
    response = epp_client().get(DISCOVERY, headers=named(name))

    assert response.status_code == 200
    assert applied(response) == f"profile={name};version=1.0"


def test_the_selected_profile_decides_what_an_object_is():
    # host is in base, RRI does not hold it: the refusal is the profile's of the request, and it names it.
    response = rri_client().get("/requestContacts/x", headers=named(BASE))

    assert response.status_code == 501
    assert response.headers["RPP-Code"] == "02307"
    assert "base" in response.json()["detail"]
    assert applied(response) == f"profile={BASE};version=1.0"


@pytest.mark.parametrize("value", [
    "profile=" + EPP + ";version=1.0, other=?1",            # an extra member is ignored
    "profile=" + EPP + ";version=1.0;extra=2",              # so is an extra parameter
    "profile=" + EPP + ";  version=1.0",                    # whitespace is the grammar's
    "profile=" + EPP + ";version=1.00",
    "extra=(1 2), profile=" + EPP + ";version=1.000",
])
def test_the_value_is_any_structured_dictionary_with_the_profile_and_its_version(value):
    response = epp_client().get(DISCOVERY, headers={**HEADERS, "RPP-Profile": value})

    assert response.status_code == 200
    assert applied(response) == f"profile={EPP};version=1.0"


@pytest.mark.parametrize("value, code", [
    ("", "02003"),                                          # no profile member
    ("version=1.0", "02003"),
    ("profile=" + EPP, "02003"),                            # no version
    ("profile=" + EPP + ";version=1", "02005"),             # an Integer is not a Decimal
    ("profile=" + EPP + ";version=\"1.0\"", "02005"),
    ("profile=\"" + EPP + "\";version=1.0", "02005"),       # a String is not a Token
    ("profile=?1;version=1.0", "02005"),
    ("profile=(a b);version=1.0", "02005"),
    ("profile=" + EPP + ";version=1.0,", "02005"),          # not an SF Dictionary
    ("profile=;version=1.0", "02005"),
])
def test_a_value_that_is_not_one_the_header_defines_is_a_400(value, code):
    response = epp_client().get(DISCOVERY, headers={**HEADERS, "RPP-Profile": value})

    assert response.status_code == 400
    assert response.headers["RPP-Code"] == code
    assert response.headers["Content-Type"].startswith("application/problem+json")
    assert applied(response) is None


def test_the_header_given_twice_is_a_400():
    response = epp_client().get(
        DISCOVERY, headers=[*named(EPP).items(), ("RPP-Profile", f"profile={BASE};version=1.0")])

    assert response.status_code == 400
    assert response.headers["RPP-Code"] == "02005"


@pytest.mark.parametrize("client, profile, version", [
    (epp_client(), RRI, "1.0"),             # known, not offered here
    (rri_client(), EPP, "1.0"),
    (epp_client(), "nope", "1.0"),          # unknown
    (epp_client(), EPP, "2.0"),             # unknown version
    (epp_client(), EPP, "1.1"),
    (epp_client(), EPP, "0.0"),
])
def test_a_profile_or_version_the_server_does_not_offer_is_a_400_with_a_range_error(client, profile, version):
    response = client.get(DISCOVERY, headers=named(profile, version))

    assert response.status_code == 400
    assert response.headers["RPP-Code"] == "02004"
    assert profile in response.json()["detail"] or version in response.json()["detail"]
    assert applied(response) is None


def test_a_version_is_compared_as_a_decimal_so_1_10_is_1_1(monkeypatch):
    # The Decimal problem of RFC 9651: 1.10 and 1.1 are one number. No profile has version 1.1 here, so 1.10 is refused.
    response = epp_client().get(DISCOVERY, headers=named(EPP, "1.10"))

    assert response.status_code == 400
    assert response.headers["RPP-Code"] == "02004"


@pytest.mark.parametrize("headers", [
    {"Accept": MEDIA_TYPE + f";profile={EPP};profile-version=1.0"},
    {"Accept": MEDIA_TYPE + ";Profile-Version=1.0"},
    {"Accept": f"text/html, {MEDIA_TYPE};q=0.8; profile=\"{EPP}\""},
    {"Content-Type": MEDIA_TYPE + f";profile={EPP}"},
])
def test_profile_parameters_of_the_media_type_mean_both_methods_are_in_use(headers):
    response = epp_client().get(DISCOVERY, headers={**named(EPP), **headers})

    assert response.status_code == 400
    assert response.headers["RPP-Code"] == "02001"
    assert applied(response) is None


def test_other_media_type_parameters_and_quoted_text_are_not_profile_parameters():
    headers = {**HEADERS, "Accept": MEDIA_TYPE + ';q=0.9;charset=utf-8;x="a;profile=b"'}

    assert epp_client().get(DISCOVERY, headers=headers).status_code == 200


def test_a_problem_detail_after_the_selection_names_the_profile():
    response = rri_client().get("/hosts/ns1.example.de", headers=named(RRI))

    assert response.status_code == 501
    assert applied(response) == f"profile={RRI};version=1.0"


@pytest.mark.parametrize("path, headers, status", [
    ("/hosts/a/b/c/d", HEADERS, 404),                                              # no operation serves it
    ("/hosts/ns1.example.de", {"Accept": MEDIA_TYPE, **{"RPP-Profile": f"profile={RRI};version=1.0"}}, 401),
])
def test_no_profile_is_selected_for_an_unrouted_path_or_before_the_authentication(path, headers, status):
    response = rri_client().get(path, headers=headers)

    assert response.status_code == status
    assert applied(response) is None


def test_a_bad_header_on_an_unrouted_path_is_the_404_of_the_router():
    response = rri_client().get("/hosts/a/b/c/d", headers={**HEADERS, "RPP-Profile": "x"})

    assert response.status_code == 404


def test_the_profiles_endpoint_names_the_applied_profile_not_the_one_it_reads():
    response = epp_client().get(f"/profiles/{BASE}", headers=named(EPP))

    assert response.status_code == 200
    assert applied(response) == f"profile={EPP};version=1.0"


@pytest.mark.parametrize("key", ["epp", "rri", "base"])
def test_the_value_of_the_response_header_parses_back_to_the_profile(key):
    profile = PROFILES[key]

    assert profile_header.parse([profile_header.format_profile(profile)]) == (profile.name, profile_header.Decimal(profile.version))
