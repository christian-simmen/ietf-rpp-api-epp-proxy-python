from dataclasses import dataclass

from rpp.schema.offered_preset import OfferedPreset


@dataclass(frozen=True)
class PresetSelection:
    """The presets of one request. `request` is the preset the request is read under: its parsing, checking, routing
    and the backend command. `response` is the one the response is under: what it shows and its media type. Core §Media Type
    Signalling keeps them apart (the `Content-Type` and the `Accept`); header signalling has one preset for both.
    """
    request: OfferedPreset
    response: OfferedPreset

    @classmethod
    def of(cls, preset: OfferedPreset) -> "PresetSelection":
        return cls(request=preset, response=preset)
