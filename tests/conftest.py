"""Chooses the app under test before any test module composes it (docs/agents/testing.project.md#test-environments)."""
import os

from tests.helper.test_environment import config_file, selected_name

os.environ.setdefault("RPP_CONFIG_FILE", config_file(selected_name()))

import pytest  # noqa: E402

from rpp.schema import validator  # noqa: E402


@pytest.fixture(autouse=True)
def lazy_schemas(request, monkeypatch):
    """A test runs like production: a validator the app did not build is `SchemaNotBuilt`. A test that maps without an app
    (a mapper called with the extensions it is given) opts in to building on first use with `@pytest.mark.lazy_schemas`
    or a module-level `pytestmark`."""
    monkeypatch.setattr(validator, "LAZY_BUILD", request.node.get_closest_marker("lazy_schemas") is not None)
