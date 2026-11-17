from rpp.dto.rpp_preset import RPPPreset
from rpp.mapping.shared.extension import extension_to_rpp
from rpp.mapping.shared.preset_references import preset_references, profile_references
from rpp.schema.offered_preset import OfferedPreset
from rpp.schema.schema_scope import SchemaScope


def preset_to_dto(preset: OfferedPreset) -> RPPPreset:
    """The Preset Data Object (json §Preset Data Object) of an offered preset, flattened, without its onDemand `schema`."""
    definition = preset.definition
    return RPPPreset(
        id=definition.id, name=definition.name, description=definition.description, version=definition.version,
        rpp_version=definition.rpp_version, url=definition.url,
        base_presets=preset_references(definition.base_presets) or None,
        extensions=[extension_to_rpp(extension) for extension in preset.extensions],
        profiles=profile_references(preset.profiles), bound_profiles=profile_references(preset.bound_profiles),
        default_preset=preset.default)


def model_to_rpp(preset: OfferedPreset, scope: SchemaScope, schema: dict | None = None) -> dict:
    """The read representation of an offered preset; with `schema`, the Preset Schema embedded (`includeElements=schema`)."""
    dto = preset_to_dto(preset)
    dto.schema = schema
    rpp = dto.to_rpp()
    scope.validate("preset.read", rpp)
    return rpp
