"""Chooses the app under test before any test module composes it (docs/agents/testing.project.md#test-environments)."""
import os

from tests.helper.test_environment import config_file, selected_name

os.environ.setdefault("RPP_CONFIG_FILE", config_file(selected_name()))

# The tests map without an app (a mapper called with the extensions it is given): a validator the app did not build is built
# on first use. The app itself never does that, and its tests switch this off to prove it (test_profile_schemas.py).
from rpp.schema import validator  # noqa: E402

validator.LAZY_BUILD = True
