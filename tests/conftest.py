"""Chooses the app under test before any test module composes it (docs/agents/testing.project.md#test-environments)."""
import os

from tests.helper.test_environment import config_file, selected_name

os.environ.setdefault("RPP_CONFIG_FILE", config_file(selected_name()))

import pytest  # noqa: E402

from rpp.schema import effective_schema, validator  # noqa: E402


@pytest.fixture(autouse=True, scope="module")
def fresh_schema_cache():
    """Each module starts with no schema built, so a strict test finds only what an app of its module built."""
    saved = validator._effective, effective_schema._effective
    validator._effective, effective_schema._effective = {}, {}
    yield
    validator._effective, effective_schema._effective = saved


@pytest.fixture(autouse=True)
def lazy_schemas(request, monkeypatch):
    """A test runs like production: a validator the app did not build is `SchemaNotBuilt`. A test that maps without an app
    (a mapper called with the extensions it is given) opts in to building on first use with `@pytest.mark.lazy_schemas`
    or a module-level `pytestmark`."""
    lazy = request.node.get_closest_marker("lazy_schemas") is not None
    monkeypatch.setattr(validator, "LAZY_BUILD", lazy)
    if lazy:  # what a lazy test builds is dropped after it
        monkeypatch.setattr(validator, "_effective", dict(validator._effective))
        monkeypatch.setattr(effective_schema, "_effective", dict(effective_schema._effective))
