from sqlalchemy import delete
from sqlalchemy.orm import Session

from extensions.planet_atmosphere.core.model.atmosphere import Atmosphere
from extensions.planet_atmosphere.core.model.atmosphere_changes import AtmosphereChanges
from extensions.planet_atmosphere.core.model.atmosphere_rules import atmosphere_violations
from registry_adapter.sqlite.extensions.planet_atmosphere.models.atmosphere_row import AtmosphereRow
from registry_adapter.sqlite.member_refused import MemberRefused


class AtmosphereHook:
    """The atmosphere of a planet, in the unit of work of the planet's gateway (`MemberHook`)."""

    def create(self, session: Session, object_id: str, value: Atmosphere) -> None:
        violations = atmosphere_violations(value)
        if violations:
            raise MemberRefused("; ".join(violations))
        session.merge(AtmosphereRow(planet_id=object_id, pressure=value.pressure, dominant_gas=value.dominantGas))

    def replace(self, session: Session, object_id: str, value: Atmosphere | None) -> None:
        if value is None:
            self.delete(session, object_id)
        else:
            self.create(session, object_id, value)

    def change(self, session: Session, object_id: str, changes: AtmosphereChanges) -> None:
        if changes.removed:
            self.delete(session, object_id)
        elif changes.atmosphere is not None:
            self.create(session, object_id, changes.atmosphere)

    def read(self, session: Session, object_id: str) -> Atmosphere | None:
        row = session.get(AtmosphereRow, object_id)
        return None if row is None else Atmosphere(pressure=row.pressure, dominantGas=row.dominant_gas)

    def delete(self, session: Session, object_id: str) -> None:
        session.execute(delete(AtmosphereRow).where(AtmosphereRow.planet_id == object_id))
