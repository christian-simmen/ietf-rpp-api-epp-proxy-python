"""How the integration runner names the profile of each step."""
import pytest

from tests.helper.test_environment import EnvironmentError, load, with_profiles

ENV = load("epp-docker", with_credentials=False)
EPP = "profile=urn:ietf:params:rpp:profile:epp-compatibility;version=1.0"
BASE = "profile=urn:ietf:params:rpp:profile:base;version=1.0"


def headers_of(case, step=0):
    return with_profiles(case, ENV)["steps"][step]["request"]["headers"]


def step(**extra):
    return {"request": {"method": "GET", "url": "/x", "headers": {"Accept": "a"}}, **extra}


def test_a_step_names_the_profile_of_the_environment():
    assert headers_of({"steps": [step()]})["RPP-Profile"] == EPP


def test_the_case_and_then_the_step_name_another():
    case = {"profile": "base", "steps": [step(), step(profile="epp")]}

    assert headers_of(case)["RPP-Profile"] == BASE
    assert headers_of(case, 1)["RPP-Profile"] == EPP
    assert "profile" not in with_profiles(case, ENV)["steps"][1]


@pytest.mark.parametrize("name", ["RPP-Profile", "rpp-profile"])
def test_a_header_the_step_sets_itself_is_the_only_one(name):
    case = {"steps": [{"request": {"method": "GET", "url": "/x", "headers": {name: "garbage"}}}]}

    headers = headers_of(case)
    assert headers == {name: "garbage"}


def test_an_unknown_profile_key_is_an_error():
    with pytest.raises(EnvironmentError):
        with_profiles({"steps": [step(profile="nope")]}, ENV)
