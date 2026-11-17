"""Two presets that build on each other: the preset `cycle-a` builds on `cycle-b`, which builds on `cycle-a`."""
from registration import ExtensionRegistry
from tests.helper.preset_fixtures import preset
from tests.refused_configs.data_only_extension import register_definitions

A = preset("cycle-a", base_presets=["org.example.rpp.preset.cycle-b"])
B = preset("cycle-b", base_presets=["org.example.rpp.preset.cycle-a"])


def register(registry: ExtensionRegistry) -> None:
    register_definitions(registry, "preset-cycle", presets=[A, B])
