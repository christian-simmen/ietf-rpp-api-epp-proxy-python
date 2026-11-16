"""The validators of a preset (D18) and the two steps of json §Profiles and Validation, without an app."""
import pytest
from jsonschema import ValidationError

from rpp.schema.definitions import Definitions
from rpp.schema.offered_presets import OfferedPresets
from rpp.schema.profile_constraint_violation import ProfileConstraintViolation
from rpp.schema.schema_scope import SchemaNotBuilt, SchemaScope
from tests.helper.preset_fixtures import ADMIN_ONLY, AUTH_REQUIRED, BASE, definitions_with, preset, profile

PROV_REQUIRED = profile("prov-required", constraints={"domainName.read": "profile.prov"}, defs={
    "profile.prov": {"properties": {"provMetadata": {"required": ["repositoryId"]}}}})
ONE_CONTACT = profile("one-contact", constraints={"domainName.read": "profile.one"}, defs={
    "profile.one": {"properties": {"contacts": {"maxItems": 1}}}})

READ = {"@type": "domainName", "name": "foo.example", "status": [{"@type": "domainStatus", "label": "ok"}],
        "provMetadata": {"@type": "provMetadata", "spClientId": "clientA", "crClientId": "clientA", "crDate": "2025-01-01T00:00:00Z"}}


def scope_of(*profiles, extensions=()):
    entries = [preset("p", base_presets=[BASE["id"]], profiles=[p[0] for p in profiles])]
    offered = OfferedPresets.build(definitions_with(entries, list(profiles)), ["p"], "p", {}, extensions).offered[0]
    return SchemaScope(offered.extensions, offered.applicable)


def test_without_a_profile_the_two_steps_are_the_one_validation():
    scope = SchemaScope.of()

    scope.validate_request("domainName.read", READ)
    with pytest.raises(ValueError, match="Undeclared property"):
        scope.validate_request("domainName.read", {**READ, "surprise": 1})


def test_step_one_fails_with_the_error_of_today_before_a_profile_is_asked():
    scope = scope_of(ADMIN_ONLY)

    with pytest.raises(ValidationError):
        scope.validate_request("domainName.create", {"@type": "domainName", "name": "a.example", "contacts": [{}]})
    with pytest.raises(ValueError, match="Undeclared"):
        scope.validate_request("domainName.create", {"@type": "domainName", "name": "a.example", "x": 1})


def test_step_two_fails_with_the_profile_the_path_and_a_reason_that_holds_no_value_of_the_request():
    scope = scope_of(ADMIN_ONLY)
    body = {"@type": "domainName", "name": "a.example",
            "contacts": [{"label": "secret-label", "object": {"@type": "contact", "id": "C-1"}}]}

    with pytest.raises(ProfileConstraintViolation) as error:
        scope.validate_request("domainName.create", body)

    assert error.value.profile == ADMIN_ONLY[0]
    assert error.value.path == "$.contacts[0].label"
    assert "secret-label" not in error.value.reason and ADMIN_ONLY[0] in error.value.reason


def test_the_profile_is_the_one_whose_sub_schema_failed_among_several():
    scope = scope_of(ADMIN_ONLY, AUTH_REQUIRED)
    contact = {"label": "admin", "object": {"@type": "contact", "id": "C-1"}}

    with pytest.raises(ProfileConstraintViolation) as missing:
        scope.validate_request("domainName.create", {"@type": "domainName", "name": "a.example", "contacts": [contact]})
    with pytest.raises(ProfileConstraintViolation) as label:
        scope.validate_request("domainName.create", {"@type": "domainName", "name": "a.example", "authInfo": {
            "@type": "authInfo", "method": "password", "authdata": "x"}, "contacts": [{**contact, "label": "tech"}]})

    assert missing.value.profile == AUTH_REQUIRED[0] and "authInfo" in missing.value.reason
    assert label.value.profile == ADMIN_ONLY[0]


def test_an_object_a_profile_does_not_constrain_is_not_asked():
    scope_of(ADMIN_ONLY).validate_request("host.create", {"@type": "host", "hostName": "ns.example"})


def test_a_patched_object_is_not_refused_for_a_server_managed_member_but_a_created_one_is():
    scope = scope_of(PROV_REQUIRED)

    scope.validate_request("domainName.read", READ, patched=True)           # the server's own metadata, not the client's
    with pytest.raises(ProfileConstraintViolation, match="repositoryId"):
        scope.validate_request("domainName.read", READ)


def test_a_patched_object_is_refused_for_what_the_client_changed():
    scope = scope_of(ONE_CONTACT)
    contact = {"label": "admin", "object": {"@type": "contact", "id": "C-1"}}

    with pytest.raises(ProfileConstraintViolation) as error:
        scope.validate_request("domainName.read", {**READ, "contacts": [contact, contact]}, patched=True)

    assert error.value.profile == ONE_CONTACT[0] and error.value.path == "$.contacts"


def test_the_published_composition_and_the_validators_are_those_of_the_preset_not_of_the_process():
    with_profile, without = scope_of(ADMIN_ONLY), scope_of()
    body = {"@type": "domainName", "name": "a.example",
            "contacts": [{"label": "tech", "object": {"@type": "contact", "id": "C-1"}}]}

    without.validate_request("domainName.create", body)
    with pytest.raises(ProfileConstraintViolation):
        with_profile.validate_request("domainName.create", body)
    without.validate_request("domainName.create", body)       # building another scope changed nothing of the first


def test_a_definition_the_preset_does_not_have_is_not_built_not_a_refusal_of_the_request():
    scope = scope_of()

    with pytest.raises(SchemaNotBuilt):
        scope.validate("requestContact.create", {})


def test_the_extensions_of_a_preset_are_the_ones_it_validates_for():
    rri = Definitions.load().presets["rri"]
    offered = OfferedPresets.build(Definitions.load(), ["rri"], "rri", {}, ("de.denic.rpp.rri",)).offered[0]
    scope = SchemaScope(offered.extensions, offered.applicable)

    assert scope.extensions == ("de.denic.rpp.rri",) and rri.id == "de.denic.rpp.preset.rri"
    scope.validate("requestContact.create", {"@type": "requestContact", "id": "DENIC-1000022-GR",
                                             "uriTemplate": "https://example.com/c?d={Alabel}"})
