from rpp.dto.rpp_extension import RPPExtension
from rpp.schema.rpp_extension import RppExtension


def extension_to_rpp(extension: RppExtension) -> RPPExtension:
    """The Extension Object (json §6.2.12) of an extension, as discovery and a profile state it."""
    return RPPExtension(name=extension.name, id=extension.id, version=extension.version, url=extension.url)
