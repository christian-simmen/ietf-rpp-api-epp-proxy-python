"""The rule of json §Profile Schema: a sub-schema declares no property its target does not (#178 review)."""
import pytest

from rpp.schema.effective_schema import bundle_definitions
from rpp.schema.profile_schema_walk import undeclared

BUNDLE = bundle_definitions()


@pytest.mark.parametrize("sub, expected", [
    ({"dependentSchemas": {"name": {"properties": {"surprise": {}}}}}, ["$.surprise"]),
    ({"properties": {"contacts": {"prefixItems": [{"properties": {"colour": {}}}]}}}, ["$.contacts[0].colour"]),
    ({"properties": {"surprise": {}}}, ["$.surprise"]),
    ({"properties": {"contacts": {"prefixItems": [{"properties": {"label": {"enum": ["admin"]}}}]}}}, []),
    ({"dependentSchemas": {"name": {"properties": {"authInfo": {"type": "object"}}}}}, []),
])
def test_dependent_schemas_and_prefix_items_are_walked(sub, expected):
    assert undeclared(sub, {}, BUNDLE["domainName.create"], BUNDLE) == expected
