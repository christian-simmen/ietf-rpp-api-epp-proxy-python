from rpp.http.header_preset_signalling import HeaderPresetSignalling
from rpp.http.media_type_preset_signalling import MediaTypePresetSignalling
from rpp.schema.offered_presets import OfferedPresets

HEADER_SIGNALLING = "header"
MEDIA_TYPE_SIGNALLING = "media-type"

_METHODS = {HEADER_SIGNALLING: HeaderPresetSignalling, MEDIA_TYPE_SIGNALLING: MediaTypePresetSignalling}


def preset_signalling(method: str, presets: OfferedPresets):
    """The signalling method of `rpp_preset_signalling` (core §Preset Signalling): it selects the preset of a request and
    shows the applied one in the response."""
    if method not in _METHODS:
        raise ValueError(f"rpp_preset_signalling must be one of {', '.join(_METHODS)}, not {method!r}")
    return _METHODS[method](presets)
