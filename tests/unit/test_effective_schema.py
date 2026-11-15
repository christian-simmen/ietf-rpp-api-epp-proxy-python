"""The injection of `"unevaluatedProperties": false` (json §4.9.1, guidelines §8.6) on schemas of known shape."""
import copy

from jsonschema import Draft202012Validator

from rpp.schema import effective_schema


def injected(schema):
    schema = copy.deepcopy(schema)
    effective_schema._inject(schema)
    return Draft202012Validator(schema)


def test_a_member_the_parent_declares_is_evaluated_through_a_one_of_branch_and_another_is_refused():
    schema = {"type": "object", "properties": {"a": {}}, "oneOf": [{"type": "object", "properties": {"b": {}}}]}
    validator = injected(schema)

    assert validator.is_valid({"a": 1, "b": 2})
    assert not validator.is_valid({"a": 1, "b": 2, "c": 3})
    assert not validator.is_valid({"a": 1, "c": 3})


def test_no_node_reached_through_an_applicator_has_the_keyword_but_what_is_below_it_has():
    schema = {"type": "object", "properties": {"a": {}}, "allOf": [{"type": "object", "properties": {
        "b": {"type": "object", "properties": {"x": {}}}, "c": {"type": "array", "items": {"type": "object", "properties": {"y": {}}}}}}],
        "anyOf": [{"type": "object", "properties": {"d": {}}}], "if": {"type": "object", "properties": {"a": {"const": 1}}},
        "then": {"type": "object", "properties": {"e": {}}}}
    copied = copy.deepcopy(schema)
    effective_schema._inject(copied)

    assert copied["unevaluatedProperties"] is False
    for branch in (copied["allOf"][0], copied["anyOf"][0], copied["then"]):
        assert "unevaluatedProperties" not in branch
    assert "unevaluatedProperties" not in copied["if"]                          # a condition is not entered
    assert copied["allOf"][0]["properties"]["b"]["unevaluatedProperties"] is False
    assert copied["allOf"][0]["properties"]["c"]["items"]["unevaluatedProperties"] is False
    validator = Draft202012Validator(copied)
    assert validator.is_valid({"a": 1, "b": {"x": 1}, "c": [{"y": 1}], "d": 1, "e": 1})
    assert not validator.is_valid({"a": 1, "b": {"x": 1, "z": 1}})
    assert not validator.is_valid({"a": 1, "c": [{"y": 1, "z": 1}]})


def test_free_keys_and_an_explicit_keyword_stay_as_they_are():
    free = injected({"type": "object", "properties": {"rdata": {"type": "object", "additionalProperties": True}}})
    explicit = injected({"type": "object", "properties": {"x": {"type": "object", "unevaluatedProperties": True}}})

    assert free.is_valid({"rdata": {"anything": 1}}) and not free.is_valid({"other": 1})
    assert explicit.is_valid({"x": {"anything": 1}}) and not explicit.is_valid({"other": 1})
