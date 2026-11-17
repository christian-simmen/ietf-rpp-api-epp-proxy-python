"""How the integration runner resolves the placeholders of the preset headers: it adds nothing of its own."""
from dataclasses import replace
from datetime import datetime

import pytest

from tests.integration.file_cases import process_placeholders
from tests.helper.test_environment import EnvironmentError, load, with_rpp_headers

ENV = load("epp-docker", with_credentials=False)
MEDIA = replace(ENV, preset_signalling="media-type")
EPP = "urn:ietf:params:rpp:preset:epp-compatible"
RPP = "application/rpp+json"
PRESET_RRI = 'application/rpp+json; preset="de.denic.rpp.preset.rri"; preset-version="1.0"'
PRESET = f'{RPP}; preset="{EPP}"; preset-version="1.0"'
ALL = {"RPP-Preset": "{rpp:preset}", "Accept": "{rpp:accept}", "Content-Type": "{rpp:content-type}"}


def headers_of(headers, env=ENV):
    case = {"steps": [{"request": {"method": "GET", "url": "/x", "headers": headers}}]}
    return with_rpp_headers(case, env)["steps"][0]["request"]["headers"]


def test_the_header_method_resolves_the_profile_header_and_the_plain_media_type():
    assert headers_of(ALL) == {"RPP-Preset": f"preset={EPP};version=1.0", "Accept": RPP, "Content-Type": RPP}


def test_the_media_type_method_omits_the_header_and_puts_the_profile_in_the_media_type():
    assert headers_of(ALL, MEDIA) == {"Accept": PRESET, "Content-Type": PRESET}


@pytest.mark.parametrize("env", [ENV, MEDIA])
def test_nothing_is_added_to_a_request_that_does_not_state_it(env):
    assert headers_of({"Authorization": "x"}, env) == {"Authorization": "x"}
    assert headers_of({}, env) == {}


@pytest.mark.parametrize("env", [ENV, MEDIA])
def test_a_literal_value_is_sent_as_it_is(env):
    own = {"RPP-Preset": "garbage", "Accept": "text/html", "Content-Type": "application/epp+xml"}

    assert headers_of(own, env) == own


def test_the_environment_decides_the_profile():
    base = replace(ENV, rpp_preset="base")

    assert headers_of({"RPP-Preset": "{rpp:preset}"}, base) == {
        "RPP-Preset": "preset=urn:ietf:params:rpp:preset:base;version=1.0"}


@pytest.mark.parametrize("value", ["{rpp:nope}", "x {rpp:accept}"])
def test_an_unknown_placeholder_or_one_inside_a_value_is_an_error(value):
    with pytest.raises(EnvironmentError):
        headers_of({"Accept": value})


def test_the_signalling_of_the_config_is_a_fact_of_the_environment():
    # each environment reads it from its own config, which a fact stated in the descriptor could not follow
    assert ENV.facts["preset_signalling"] == "header"
    assert load("rri-mtest", with_credentials=False).facts["preset_signalling"] == "media-type"


def test_the_placeholders_of_an_environment_follow_the_signalling_of_its_config():
    mtest = load("rri-mtest", with_credentials=False)

    assert headers_of(ALL, mtest) == {"Accept": PRESET_RRI, "Content-Type": PRESET_RRI}


@pytest.mark.parametrize("where", [{"url": "/x/{rpp:accept}"}, {"body_json": {"a": ["{rpp:preset}"]}},
                                   {"response": {"headers": {"Content-Type": "{rpp:content-type}"}}}])
def test_a_placeholder_left_after_the_headers_are_resolved_is_an_error(where):
    case = {"test_id": "t", "steps": [{"request": {"method": "GET", "url": "/x", "headers": {}}, **where}]}
    with pytest.raises(EnvironmentError, match="rpp"):
        process_placeholders(with_rpp_headers(case, ENV), ENV, started=datetime.now())


DEMO = load("sqlite-demo-bound", with_credentials=False)
DEMO_HEADER = replace(DEMO, preset_signalling="header")
ATMOSPHERE = "org.example.rpp.preset.planets-atmosphere"


def test_a_placeholder_with_a_key_stands_for_that_preset_of_the_config_in_either_method():
    keyed = {"RPP-Preset": "{rpp:preset:planets-atmosphere}", "Accept": "{rpp:accept:planets-atmosphere}",
             "Content-Type": "{rpp:content-type:planets-atmosphere}"}

    assert headers_of(keyed, DEMO_HEADER) == {"RPP-Preset": f"preset={ATMOSPHERE};version=1.0", "Accept": RPP, "Content-Type": RPP}
    typed = f'{RPP}; preset="{ATMOSPHERE}"; preset-version="1.0"'
    assert headers_of(keyed, DEMO) == {"Accept": typed, "Content-Type": typed}


def test_a_placeholder_without_a_key_is_the_preset_of_the_descriptor():
    assert headers_of({"RPP-Preset": "{rpp:preset}"}, DEMO_HEADER) == {
        "RPP-Preset": "preset=org.example.rpp.preset.planets;version=1.0"}


def test_a_key_the_config_does_not_offer_a_definition_of_is_an_error():
    with pytest.raises(EnvironmentError, match="no preset 'nope'"):
        headers_of({"Accept": "{rpp:accept:nope}"}, DEMO)
