"""One extension in two versions: the preset `clash` builds on `clash-a`, which contains the planets extension 1.0, and on
`clash-b`, which contains the planets extension 2.0."""
from registration import ExtensionRegistry
from tests.helper.preset_fixtures import preset
from tests.refused_configs.data_only_extension import register_definitions

PLANETS = "org.example.rpp.extension.planets"

A = preset("clash-a", extensions=[(PLANETS, "1.0")])
B = preset("clash-b", extensions=[(PLANETS, "2.0")])
CLASH = preset("clash", base_presets=["org.example.rpp.preset.clash-a", "org.example.rpp.preset.clash-b"])


def register(registry: ExtensionRegistry) -> None:
    register_definitions(registry, "version-clash", presets=[A, B, CLASH])
