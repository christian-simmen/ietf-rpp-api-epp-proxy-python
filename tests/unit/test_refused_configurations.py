"""The configurations that must not start (#180): the app refuses each at start and names the conflict, with both sides of
it. The definitions of a cycle and of two versions of one extension are test-only (tests/refused_configs/), the shipped
demo extensions define valid ones only."""
import os
import subprocess
import sys

import pytest

from main import compose
from settings.load_settings import load_settings
from tests.helper.test_environment import REPOSITORY

REFUSED = REPOSITORY / "tests" / "refused_configs"
P = "org.example.rpp.preset."
Q = "org.example.rpp.profile."
E = "org.example.rpp.extension."

CASES = {
    "missing-extension.yaml": f"The profile {Q}habitable-atmospheres requires the extension {E}planet-atmosphere, "
                              f"which the preset {P}planets does not contain",
    "missing-extension-transitive.yaml": f"The profile {Q}habitable-rocky-planets requires the extension {E}planet-atmosphere, "
                                         f"which the preset {P}planets does not contain",
    "preset-cycle.yaml": f"The preset {P}cycle-a builds on itself: {P}cycle-a -> {P}cycle-b -> {P}cycle-a",
    "profile-cycle.yaml": f"The profile {Q}cycle-x builds on itself: {Q}cycle-x -> {Q}cycle-y -> {Q}cycle-x",
    "version-clash.yaml": f"The preset {P}clash contains the extension {E}planets in the versions 1.0 and 2.0",
}


@pytest.mark.parametrize("name, message", CASES.items())
def test_a_conflicting_configuration_does_not_start_and_names_the_conflict(name, message):
    with pytest.raises(ValueError) as refused:
        compose(load_settings(str(REFUSED / name)))

    assert message in str(refused.value)


def test_every_refused_configuration_has_a_case():
    assert {path.name for path in REFUSED.glob("*.yaml")} == set(CASES)


def test_the_server_process_exits_with_the_conflict_on_stderr():
    result = subprocess.run(
        [sys.executable, "-I", "-c", "import sys; sys.path[:0] = [sys.argv[1], sys.argv[2]]; import main",
         str(REPOSITORY), str(REPOSITORY / "src")],
        env={**os.environ, "RPP_CONFIG_FILE": str(REFUSED / "preset-cycle.yaml")}, cwd=str(REPOSITORY / "src"),
        capture_output=True, text=True, timeout=120)

    assert result.returncode != 0
    assert CASES["preset-cycle.yaml"] in result.stderr
