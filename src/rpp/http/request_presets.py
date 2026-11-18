from core.capabilities.backend_profile import BackendProfile
from rpp.schema.offered_preset import OfferedPreset
from rpp.schema.offered_presets import OfferedPresets
from rpp.http.preset_selection import PresetSelection
from rpp.schema.preset_schemas import PresetSchemas
from rpp.schema.request_schemas import RequestSchemas
from rpp.schema.schema_scope import SchemaScope


class RequestPresets:
    """The backend profile, and the schema scope, as a request under each offered preset sees them, made once when the app is
    built.

    The extensions of the backend profile are those of the selected preset, so the combined schema holds only them. The
    objects are those the backend holds: the preset names none (data-objects: the objects of Discovery stay as they are).
    """

    def __init__(self, backend: BackendProfile, presets: OfferedPresets, schemas: PresetSchemas):
        self._by_id = {
            item.id: (backend.with_changes({"extensions": list(item.extension_ids)}), schemas.scope_of(item))
            for item in presets.offered
        }

    def profile_of(self, preset: OfferedPreset) -> BackendProfile:
        return self._by_id[preset.id][0]

    def scope_of(self, preset: OfferedPreset) -> SchemaScope:
        return self._by_id[preset.id][1]

    def scopes(self) -> tuple[SchemaScope, ...]:
        return tuple(scope for _, scope in self._by_id.values())

    def schemas(self, selection: PresetSelection) -> RequestSchemas:
        """The schemas a request under `selection` is validated with: those of its request preset and its response preset."""
        return RequestSchemas(request=self.scope_of(selection.request), response=self.scope_of(selection.response),
                              scopes=self.scopes())
