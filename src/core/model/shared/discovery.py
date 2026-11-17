from dataclasses import dataclass


@dataclass(kw_only=True)
class Discovery:
    """What discovery states of the server and the backend. The presets, their profiles and extensions are RPP's and
    are not here: the mapper takes them from the offered presets."""
    version: str
    base_url: str
    tlds: list[str]
    environment_name: str
    environment_status: str
    objects: list[str]
    datetime: str
