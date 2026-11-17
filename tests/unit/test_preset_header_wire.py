"""Preset signalling with the RPP-Preset header (core §14.2): the selection, its refusals and the response header."""
import pytest

from rpp.http import preset_header
from tests.helper.presets import EPP_PRESETS, RRI_PRESETS
from tests.unit.test_presets_wire import BASE, EPP, RRI, epp_client, rri_client
from tests.unit.test_rri_wire import HEADERS, MEDIA_TYPE

DISCOVERY = "/.well-known/rpp"


def named(preset, version="1.0", **extra):
    return {**HEADERS, "RPP-Preset": f"preset={preset};version={version}", **extra}


def applied(response):
    return response.headers.get("RPP-Preset")


def test_a_request_without_the_header_gets_the_default_profile_and_names_it():
    response = epp_client().get(DISCOVERY, headers=HEADERS)

    assert response.status_code == 200
    assert applied(response) == f"preset={EPP};version=1.0"


@pytest.mark.parametrize("name", [BASE, EPP])
def test_the_header_selects_an_offered_profile(name):
    response = epp_client().get(DISCOVERY, headers=named(name))

    assert response.status_code == 200
    assert applied(response) == f"preset={name};version=1.0"


def test_the_selected_preset_decides_what_an_object_is():
    # requestContact is not in the base preset (core RC4): a 400 with the code of any content that does not conform to it,
    # and it names the preset of the request.
    response = rri_client().get("/requestContacts/x", headers=named(BASE))

    assert response.status_code == 400
    assert response.headers["RPP-Code"] == "02001"
    assert "base" in response.json()["detail"]
    assert applied(response) == f"preset={BASE};version=1.0"


@pytest.mark.parametrize("value", [
    "preset=" + EPP + ";version=1.0, other=?1",            # an extra member is ignored
    "preset=" + EPP + ";version=1.0;extra=2",              # so is an extra parameter
    "preset=" + EPP + ";  version=1.0",                    # whitespace is the grammar's
    "preset=" + EPP + ";version=1.00",
    "extra=(1 2), preset=" + EPP + ";version=1.000",
])
def test_the_value_is_any_structured_dictionary_with_the_profile_and_its_version(value):
    response = epp_client().get(DISCOVERY, headers={**HEADERS, "RPP-Preset": value})

    assert response.status_code == 200
    assert applied(response) == f"preset={EPP};version=1.0"


@pytest.mark.parametrize("value, code", [
    ("", "02003"),                                          # no preset member
    ("version=1.0", "02003"),
    ("preset=" + EPP, "02003"),                            # no version
    ("preset=" + EPP + ";version=1", "02005"),             # an Integer is not a Decimal
    ("preset=" + EPP + ";version=\"1.0\"", "02005"),
    ("preset=\"" + EPP + "\";version=1.0", "02005"),       # a String is not a Token
    ("preset=?1;version=1.0", "02005"),
    ("preset=(a b);version=1.0", "02005"),
    ("preset=" + EPP + ";version=1.0,", "02005"),          # not an SF Dictionary
    ("preset=;version=1.0", "02005"),
])
def test_a_value_that_is_not_one_the_header_defines_is_a_400(value, code):
    response = epp_client().get(DISCOVERY, headers={**HEADERS, "RPP-Preset": value})

    assert response.status_code == 400
    assert response.headers["RPP-Code"] == code
    assert response.headers["Content-Type"].startswith("application/problem+json")
    assert applied(response) is None


def test_field_lines_are_combined_into_one_dictionary_and_a_repeated_key_is_the_last():
    other = epp_client().get(DISCOVERY, headers=[*named(EPP).items(), ("RPP-Preset", "other=1")])
    last = epp_client().get(DISCOVERY, headers=[*named(EPP).items(), ("RPP-Preset", f"preset={BASE};version=1.0")])

    assert other.status_code == 200 and applied(other) == f"preset={EPP};version=1.0"
    assert last.status_code == 200 and applied(last) == f"preset={BASE};version=1.0"


@pytest.mark.parametrize("client, preset, version", [
    (epp_client(), RRI, "1.0"),             # known, not offered here
    (rri_client(), EPP, "1.0"),
    (epp_client(), "nope", "1.0"),          # unknown
    (epp_client(), EPP, "2.0"),             # unknown version
    (epp_client(), EPP, "1.1"),
    (epp_client(), EPP, "0.0"),
])
def test_a_profile_or_version_the_server_does_not_offer_is_a_400_with_a_range_error(client, preset, version):
    response = client.get(DISCOVERY, headers=named(preset, version))

    assert response.status_code == 400
    assert response.headers["RPP-Code"] == "02004"
    assert preset in response.json()["detail"] or version in response.json()["detail"]
    assert applied(response) is None


def test_versions_1_10_and_1_1_are_one_number_so_a_profile_cannot_have_both():
    assert preset_header.parse(["preset=x;version=1.10"]) == preset_header.parse(["preset=x;version=1.1"]) \
        == ("x", preset_header.Decimal("1.1"))


def test_an_unoffered_version_1_10_is_refused():
    response = epp_client().get(DISCOVERY, headers=named(EPP, "1.10"))

    assert response.status_code == 400
    assert response.headers["RPP-Code"] == "02004"


def test_a_version_that_is_a_boolean_is_not_a_decimal():
    with pytest.raises(preset_header.PresetHeaderError) as error:
        preset_header.parse([f"preset={EPP};version"])

    assert error.value.code.value[0] == "2005"


@pytest.mark.parametrize("headers", [
    {"Accept": MEDIA_TYPE + f";preset={EPP};preset-version=1.0"},
    {"Accept": MEDIA_TYPE + ";Preset-Version=1.0"},
    {"Accept": f"text/html, {MEDIA_TYPE};q=0.8; preset=\"{EPP}\""},
    {"Content-Type": MEDIA_TYPE + f";preset={EPP}"},
    {"Accept": "application/RPP+JSON;preset=x"},
    {"Accept": f"application/ld+json, {MEDIA_TYPE};q=0.5, application/rpp+yaml;preset-version=1.0"},
])
def test_profile_parameters_of_the_media_type_mean_both_methods_are_in_use(headers):
    response = epp_client().get(DISCOVERY, headers={**named(EPP), **headers})

    assert response.status_code == 400
    assert response.headers["RPP-Code"] == "02001"
    assert applied(response) is None


def test_the_profile_parameter_of_another_media_type_is_its_own():
    headers = {**HEADERS, "Accept": MEDIA_TYPE + ', application/ld+json;preset="https://x"'}

    assert epp_client().get(DISCOVERY, headers=headers).status_code == 200


def test_other_media_type_parameters_and_quoted_text_are_not_profile_parameters():
    headers = {**HEADERS, "Accept": MEDIA_TYPE + ';q=0.9;charset=utf-8;x="a;preset=b"'}

    assert epp_client().get(DISCOVERY, headers=headers).status_code == 200


def test_a_problem_detail_after_the_selection_names_the_profile():
    response = rri_client().get("/hosts/ns1.example.de", headers=named(RRI))

    assert response.status_code == 501
    assert applied(response) == f"preset={RRI};version=1.0"


@pytest.mark.parametrize("path, headers, status", [
    ("/hosts/a/b/c/d", HEADERS, 404),                                              # no operation serves it
    ("/hosts/ns1.example.de", {"Accept": MEDIA_TYPE, **{"RPP-Preset": f"preset={RRI};version=1.0"}}, 401),
])
def test_no_profile_is_selected_for_an_unrouted_path_or_before_the_authentication(path, headers, status):
    response = rri_client().get(path, headers=headers)

    assert response.status_code == status
    assert applied(response) is None


def test_a_bad_header_on_an_unrouted_path_is_the_404_of_the_router():
    response = rri_client().get("/hosts/a/b/c/d", headers={**HEADERS, "RPP-Preset": "x"})

    assert response.status_code == 404


def test_the_profiles_endpoint_names_the_applied_profile_not_the_one_it_reads():
    response = epp_client().get(f"/presets/{BASE}", headers=named(EPP))

    assert response.status_code == 200
    assert applied(response) == f"preset={EPP};version=1.0"


@pytest.mark.parametrize("presets, identifier", [(EPP_PRESETS, EPP), (RRI_PRESETS, RRI), (EPP_PRESETS, BASE)])
def test_the_value_of_the_response_header_parses_back_to_the_preset(presets, identifier):
    preset = presets.by_id(identifier)

    assert preset_header.parse([preset_header.format_preset(preset)]) == (preset.id, preset_header.Decimal(preset.version))


def test_the_response_depends_on_the_preset_header_so_it_varies_on_it():
    assert "RPP-Preset" in epp_client().get(DISCOVERY, headers=HEADERS).headers["Vary"]
    assert "RPP-Preset" in rri_client().get("/hosts/ns1.example.de", headers=HEADERS).headers["Vary"]  # a Problem Detail


@pytest.mark.parametrize("existing, expected", [
    (None, "RPP-Preset"), ("Accept", "Accept, RPP-Preset"), ("Accept, rpp-preset", "Accept, rpp-preset"),
    ("*", "*"), ("Origin,Accept", "Origin, Accept, RPP-Preset"),
])
def test_vary_keeps_what_is_there(existing, expected):
    assert preset_header.vary_with_preset(existing) == expected


def test_a_handler_failure_that_is_a_problem_detail_names_the_profile():
    from tests.unit.test_domain_readback import AUTH, INFO_FAILED, client_with

    client = client_with([INFO_FAILED])
    response = client.get("/domainNames/foo.example", headers={**AUTH, **named(BASE)})

    assert response.status_code == 500
    assert applied(response) == f"preset={BASE};version=1.0"
    assert "RPP-Preset" in response.headers["Vary"]


def test_a_response_with_a_vary_header_gets_one_vary_header_that_lists_the_profile_too():
    import asyncio

    from rpp.http.header_preset_signalling import HeaderPresetSignalling
    from rpp.http.preset_selection import PresetSelection

    sent = []

    async def fake_send(message):
        sent.append(message)

    start = {"type": "http.response.start", "status": 200, "headers": [(b"vary", b"Accept"), (b"x", b"y")]}
    signalling = HeaderPresetSignalling(None)
    asyncio.run(signalling.announce(fake_send, PresetSelection.of(EPP_PRESETS.by_id(BASE)))(start))

    headers = sent[0]["headers"]
    assert [value for name, value in headers if name == b"vary"] == [b"Accept, RPP-Preset"]
    assert (b"x", b"y") in headers


def test_the_header_method_puts_no_parameters_in_the_content_type():
    response = epp_client().get(DISCOVERY, headers=named(BASE))

    assert response.headers["Content-Type"] == MEDIA_TYPE
