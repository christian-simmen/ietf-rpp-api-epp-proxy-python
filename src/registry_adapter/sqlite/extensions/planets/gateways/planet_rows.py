"""Reads of the planet tables that the planet and satellite gateways share."""
from typing import Mapping

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.model.shared.common import AuthInfo
from extensions.planets.core.model.planet import Planet
from extensions.planets.core.model.satellite import Satellite
from registry_adapter.sqlite.extensions.planets.models.planet_row import PlanetRow
from registry_adapter.sqlite.extensions.planets.models.planet_transfer_row import PlanetTransferRow
from registry_adapter.sqlite.extensions.planets.models.satellite_row import SatelliteRow
from registry_adapter.sqlite.member_hook import MemberHook

PENDING = "pending"


def transfer_of(session: Session, planet_id: str) -> PlanetTransferRow | None:
    return session.get(PlanetTransferRow, planet_id)


def is_pending(session: Session, planet_id: str) -> bool:
    transfer = transfer_of(session, planet_id)
    return transfer is not None and transfer.status == PENDING


def satellite_ids(session: Session, planet_id: str) -> tuple[str, ...]:
    return tuple(session.scalars(select(SatelliteRow.id).where(SatelliteRow.planet_id == planet_id).order_by(SatelliteRow.id)))


def members_of(session: Session, hooks: Mapping[str, MemberHook], object_id: str) -> dict[str, object]:
    """What the extensions that add members hold for the object, by extension id."""
    read = {extension_id: hook.read(session, object_id) for extension_id, hook in hooks.items()}
    return {extension_id: value for extension_id, value in read.items() if value is not None}


def to_planet(session: Session, row: PlanetRow, reader: str, hooks: Mapping[str, MemberHook] = {}) -> Planet:
    """The planet as `reader` may see it: the authInfo only for the sponsor."""
    return Planet(
        id=row.id, type=row.type, radius=row.radius, mass=row.mass, satellites=satellite_ids(session, row.id),
        pending_transfer=is_pending(session, row.id), roid=f"{row.id}-PLANET", clID=row.sponsor, crID=row.creator,
        crDate=row.created, upID=row.updater, upDate=row.updated, trDate=row.transferred,
        authInfo=AuthInfo(pw=row.auth_pw) if reader == row.sponsor else None,
        extensions=members_of(session, hooks, row.id))


def to_satellite(session: Session, row: SatelliteRow, planet: PlanetRow, hooks: Mapping[str, MemberHook] = {}) -> Satellite:
    return Satellite(
        id=row.id, planet=row.planet_id, orbitalPeriod=row.orbital_period, roid=f"{row.id}-SATELLITE",
        clID=planet.sponsor, crID=row.creator, crDate=row.created, upID=row.updater, upDate=row.updated,
        extensions=members_of(session, hooks, row.id))
