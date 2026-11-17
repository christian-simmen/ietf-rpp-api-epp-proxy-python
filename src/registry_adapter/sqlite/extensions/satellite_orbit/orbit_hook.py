from sqlalchemy import delete
from sqlalchemy.orm import Session

from extensions.satellite_orbit.core.model.orbit import Orbit
from extensions.satellite_orbit.core.model.orbit_changes import OrbitChanges
from extensions.satellite_orbit.core.model.orbit_rules import orbit_violations
from registry_adapter.sqlite.extensions.satellite_orbit.models.orbit_row import OrbitRow
from registry_adapter.sqlite.member_refused import MemberRefused


class OrbitHook:
    """The orbit of a satellite, in the unit of work of the satellite's gateway (`MemberHook`)."""

    def create(self, session: Session, object_id: str, value: Orbit) -> None:
        violations = orbit_violations(value)
        if violations:
            raise MemberRefused("; ".join(violations))
        session.merge(OrbitRow(satellite_id=object_id, semi_major_axis=value.semiMajorAxis,
                               eccentricity=value.eccentricity, inclination=value.inclination))

    def replace(self, session: Session, object_id: str, value: Orbit | None) -> None:
        if value is None:
            self.delete(session, object_id)
        else:
            self.create(session, object_id, value)

    def change(self, session: Session, object_id: str, changes: OrbitChanges) -> None:
        if changes.removed:
            self.delete(session, object_id)
        elif changes.orbit is not None:
            self.create(session, object_id, changes.orbit)

    def read(self, session: Session, object_id: str) -> Orbit | None:
        row = session.get(OrbitRow, object_id)
        if row is None:
            return None
        return Orbit(semiMajorAxis=row.semi_major_axis, eccentricity=row.eccentricity, inclination=row.inclination)

    def delete(self, session: Session, object_id: str) -> None:
        session.execute(delete(OrbitRow).where(OrbitRow.satellite_id == object_id))
