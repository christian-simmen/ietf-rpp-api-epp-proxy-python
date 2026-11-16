from rpp.dto.rpp_preset_reference import RPPPresetReference
from rpp.dto.rpp_profile_reference import RPPProfileReference
from rpp.schema.reference import Reference


def profile_references(references) -> list[RPPProfileReference]:
    """The reference views (`id` and `version`, json RJ6) of profiles or `Reference`s to them."""
    return [RPPProfileReference(id=item.id, version=item.version) for item in references]


def preset_references(references: tuple[Reference, ...]) -> list[RPPPresetReference]:
    return [RPPPresetReference(id=item.id, version=item.version) for item in references]
