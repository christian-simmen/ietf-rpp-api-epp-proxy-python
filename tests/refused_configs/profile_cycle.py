"""Two profiles that build on each other: `cycle-x` builds on `cycle-y`, which builds on `cycle-x`."""
from registration import ExtensionRegistry
from tests.helper.preset_fixtures import profile
from tests.refused_configs.data_only_extension import register_definitions

X = profile("cycle-x", base_profiles=["org.example.rpp.profile.cycle-y"])
Y = profile("cycle-y", base_profiles=["org.example.rpp.profile.cycle-x"])


def register(registry: ExtensionRegistry) -> None:
    register_definitions(registry, "profile-cycle", profiles=[X, Y])
