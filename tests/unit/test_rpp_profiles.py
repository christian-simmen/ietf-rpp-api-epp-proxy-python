"""The catalog of the RPP profiles a server offers: the startup checks of json §6.11, and the profile as a request
sees the backend."""
from dataclasses import replace

import pytest

from rpp.http.request_profiles import RequestProfiles
from rpp.schema import profiles as definitions
from rpp.schema.rpp_profiles import RppProfiles
from tests.helper.profiles import EPP_PROFILE, RRI_PROFILE

BASE = "io.github.pawel-kow.rpp.profile.base"
RRI_EXTENSION = "de.denic.rpp.rri"


def build(keys, default, held=()):
    return RppProfiles.build(keys, default, held)


def test_the_offered_profiles_keep_the_order_of_the_configuration_and_one_is_the_default():
    catalog = build(["rri", "base"], "base", [RRI_EXTENSION])

    assert [p.key for p in catalog.offered] == ["rri", "base"]
    assert catalog.default.key == "base"


def test_the_extensions_of_the_offered_profiles_are_each_listed_once():
    assert build(["base", "rri"], "rri", [RRI_EXTENSION]).extensions() == (RRI_EXTENSION,)


@pytest.mark.parametrize("profile, message", [
    (replace(definitions.PROFILES["epp"], base_profile="urn:ietf:params:rpp:profile:epp-compatibility"),
     "its own base profile"),
    (replace(definitions.PROFILES["epp"], extensions=(RRI_EXTENSION, RRI_EXTENSION)), "an extension twice"),
    (replace(definitions.PROFILES["epp"], extensions=("urn:example:nope",)), "does not implement"),
])
def test_a_profile_that_breaks_a_rule_of_json_6_11_stops_the_app(monkeypatch, profile, message):
    monkeypatch.setitem(definitions.PROFILES, "epp", profile)

    with pytest.raises(ValueError, match=message):
        build(["base", "epp"], "epp", [RRI_EXTENSION, "urn:ietf:params:rpp:extension:epp-compatibility"])


def test_a_base_profile_has_no_base_profile_itself(monkeypatch):
    monkeypatch.setitem(definitions.PROFILES, "base", replace(
        definitions.PROFILES["base"], base_profile="de.denic.rpp.profile.rri"))

    with pytest.raises(ValueError, match="has one itself"):
        build(["base", "rri"], "rri", [RRI_EXTENSION])


def test_a_profile_object_the_backend_does_not_hold_is_no_error():
    assert build(["base"], "base", []).default.objects == ("domainName", "contact", "host")


def test_a_request_sees_the_extensions_of_its_profile_and_the_objects_both_the_profile_and_the_backend_have():
    catalog = build(["base", "rri"], "rri", [RRI_EXTENSION])
    requests = RequestProfiles(RRI_PROFILE, catalog)

    assert requests.of(catalog.by_name(BASE)).extensions == ()
    assert requests.of(catalog.by_name(BASE)).objects == ("domainName", "contact")
    assert requests.of(catalog.default).extensions == (RRI_EXTENSION,)
    assert requests.of(catalog.default).objects == ("domainName", "contact", "requestContact")


def test_the_epp_server_offers_its_constraint_extension_under_the_epp_profile_only():
    catalog = build(EPP_PROFILE.profiles, EPP_PROFILE.default_profile, EPP_PROFILE.extensions)
    requests = RequestProfiles(EPP_PROFILE, catalog)

    assert requests.of(catalog.by_name(BASE)).extensions == ()
    assert requests.of(catalog.default).extensions == ("urn:ietf:params:rpp:extension:epp-compatibility",)
