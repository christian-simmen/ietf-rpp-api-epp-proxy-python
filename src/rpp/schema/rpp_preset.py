from dataclasses import dataclass

from rpp.schema.reference import Reference


@dataclass(frozen=True, kw_only=True, eq=False)
class RppPreset:
    """A preset (data-objects §Presets) as its definition states it: a named, versioned list of extensions and of the
    profiles its definition includes, built on its base presets. `key` is what a configuration names it by. The lists
    are the direct ones, the Data Object flattens them."""
    key: str
    id: str
    name: str
    description: str
    version: str
    rpp_version: str
    url: str | None = None
    base_presets: tuple[Reference, ...] = ()
    extensions: tuple[Reference, ...] = ()
    profiles: tuple[Reference, ...] = ()

    @property
    def reference(self) -> Reference:
        return Reference(self.id, self.version)
