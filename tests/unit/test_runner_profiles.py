"""How the integration runner resolves the placeholders of the profile headers: it adds nothing of its own."""
from dataclasses import replace
from datetime import datetime

import pytest

from tests.integration.file_cases import process_placeholders
from tests.helper.test_environment import EnvironmentError, load, with_rpp_headers

ENV = load("epp-docker", with_credentials=False)
MEDIA = replace(ENV, profile_signalling="media-type")
EPP = "urn:ietf:params:rpp:profile:epp-compatibility"
RPP = "application/rpp+json"
PROFILED = f'{RPP}; profile="{EPP}"; profile-version="1.0"'
ALL = {"RPP-Profile": "{rpp:profile}", "Accept": "{rpp:accept}", "Content-Type": "{rpp:content-type}"}


def headers_of(headers, env=ENV):
    case = {"steps": [{"request": {"method": "GET", "url": "/x", "headers": headers}}]}
    return with_rpp_headers(case, env)["steps"][0]["request"]["headers"]


def test_the_header_method_resolves_the_profile_header_and_the_plain_media_type():
    assert headers_of(ALL) == {"RPP-Profile": f"profile={EPP};version=1.0", "Accept": RPP, "Content-Type": RPP}


def test_the_media_type_method_omits_the_header_and_puts_the_profile_in_the_media_type():
    assert headers_of(ALL, MEDIA) == {"Accept": PROFILED, "Content-Type": PROFILED}


@pytest.mark.parametrize("env", [ENV, MEDIA])
def test_nothing_is_added_to_a_request_that_does_not_state_it(env):
    assert headers_of({"Authorization": "x"}, env) == {"Authorization": "x"}
    assert headers_of({}, env) == {}


@pytest.mark.parametrize("env", [ENV, MEDIA])
def test_a_literal_value_is_sent_as_it_is(env):
    own = {"RPP-Profile": "garbage", "Accept": "text/html", "Content-Type": "application/epp+xml"}

    assert headers_of(own, env) == own


def test_the_environment_decides_the_profile():
    base = replace(ENV, rpp_profile="base")

    assert headers_of({"RPP-Profile": "{rpp:profile}"}, base) == {
        "RPP-Profile": "profile=urn:ietf:params:rpp:profile:base;version=1.0"}


@pytest.mark.parametrize("value", ["{rpp:nope}", "x {rpp:accept}"])
def test_an_unknown_placeholder_or_one_inside_a_value_is_an_error(value):
    with pytest.raises(EnvironmentError):
        headers_of({"Accept": value})


def test_the_signalling_of_the_config_is_a_fact_of_the_environment():
    assert ENV.facts["profile_signalling"] == "header"


@pytest.mark.parametrize("where", [{"url": "/x/{rpp:accept}"}, {"body_json": {"a": ["{rpp:profile}"]}},
                                   {"response": {"headers": {"Content-Type": "{rpp:content-type}"}}}])
def test_a_placeholder_left_after_the_headers_are_resolved_is_an_error(where):
    case = {"test_id": "t", "steps": [{"request": {"method": "GET", "url": "/x", "headers": {}}, **where}]}
    with pytest.raises(EnvironmentError, match="rpp"):
        process_placeholders(with_rpp_headers(case, ENV), ENV, started=datetime.now())
