from dataclasses import dataclass, field

from settings.discovery_settings import DiscoverySettings
from settings.epp_settings import EppSettings
from settings.rri_settings import RriSettings

BACKENDS = ("epp", "rri")
SIGNALLING_METHODS = ("header",)  # "media-type" follows with #164


@dataclass(frozen=True)
class Settings:
    """The configuration, by the part of the proxy it is for. `main` loads it once and passes each section on.

    `backend` is the protocol the proxy speaks to the registry (`rpp_backend`): `epp` or `rri`. `profile_layers`
    are the layers of its `BackendProfile`, the generic one of the protocol first, then the server's own
    (`rpp_backend_profile`); main merges them with `lgrs`. `profile_signalling` is how a client names the profile of a
    request (`rpp_profile_signalling`, core §14): `header` (the default), or `media-type`, which is not implemented.
    """
    epp: EppSettings
    discovery: DiscoverySettings
    rri: RriSettings = field(default_factory=RriSettings)
    backend: str = "epp"
    profile_layers: tuple[dict, ...] = ()
    profile_signalling: str = "header"

    def __post_init__(self):
        if self.backend not in BACKENDS:
            raise ValueError(f"rpp_backend must be one of {', '.join(BACKENDS)}, not {self.backend!r}")
        if self.profile_signalling not in SIGNALLING_METHODS:
            raise ValueError(
                f"rpp_profile_signalling must be one of {', '.join(SIGNALLING_METHODS)}, not "
                f"{self.profile_signalling!r}")

    @property
    def lgrs(self) -> tuple[str, ...]:
        """The LGRs the backend offers for IDNs: those of the EPP IDN tables, or the one of DENIC's repertoire."""
        if self.backend == "rri":
            return (self.rri.rpp_rri_lgr,) if self.rri.rpp_rri_lgr else ()
        return tuple(sorted(self.epp.rpp_idn_lgr_tables or {}))
