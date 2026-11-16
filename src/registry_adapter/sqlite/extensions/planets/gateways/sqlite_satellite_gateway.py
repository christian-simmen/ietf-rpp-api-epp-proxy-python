from sqlalchemy.exc import IntegrityError

from core.model.shared.availability import Availability
from core.ports.replace_outcome import ReplaceOutcome
from core.result.result_code import ResultCode
from extensions.planets.core.model.satellite import Satellite
from extensions.planets.core.model.satellite_replacement import SatelliteReplacement
from registry_adapter.sqlite.clock import now
from registry_adapter.sqlite.extensions.planets.gateways.planet_rows import is_pending, to_satellite
from registry_adapter.sqlite.extensions.planets.models.planet_row import PlanetRow
from registry_adapter.sqlite.extensions.planets.models.satellite_row import SatelliteRow
from registry_adapter.sqlite.gateways.sqlite_gateway import SqliteGateway


class SqliteSatelliteGateway(SqliteGateway):
    """The satellites of the demo backend. The sponsor of a satellite is that of its planet."""

    def _missing(self, satellite_id: str, client_transaction_id):
        return self._refused(ResultCode.OBJECT_DOES_NOT_EXIST, f"The satellite {satellite_id} does not exist",
                             client_transaction_id)

    def _refusal(self, session, row: SatelliteRow, planet: PlanetRow, what: str, client_transaction_id):
        """Why the sponsor of the planet cannot change the satellite now, None where it can."""
        if planet.sponsor != self.sponsor_id:
            return self._refused(ResultCode.AUTHORIZATION_ERROR, f"Only the sponsoring client can {what} the satellite",
                                 client_transaction_id)
        if is_pending(session, planet.id):
            return self._refused(ResultCode.OBJECT_STATUS_PROHIBITS_OPERATION,
                                 f"The planet {planet.id} of the satellite has a pending transfer", client_transaction_id)
        return None

    def check(self, id, client_transaction_id=None):
        with self._context.database.transaction() as session:
            taken = session.get(SatelliteRow, id) is not None
        return self._ok(Availability(name=id, available=not taken, reason="in use" if taken else None),
                        client_transaction_id)

    def info(self, id, client_transaction_id=None):
        with self._context.database.transaction() as session:
            row = session.get(SatelliteRow, id)
            if row is None:
                return self._missing(id, client_transaction_id)
            satellite = to_satellite(row, session.get(PlanetRow, row.planet_id))
        return self._ok(satellite, client_transaction_id)

    def create(self, satellite: Satellite, client_transaction_id=None):
        try:
            with self._context.database.transaction() as session:
                planet = session.get(PlanetRow, satellite.planet)
                if planet is None:
                    return self._refused(ResultCode.OBJECT_DOES_NOT_EXIST,
                                         f"The planet {satellite.planet} does not exist", client_transaction_id)
                if planet.sponsor != self.sponsor_id:
                    return self._refused(ResultCode.AUTHORIZATION_ERROR,
                                         f"Only the sponsoring client of the planet {planet.id} can create its satellite",
                                         client_transaction_id)
                session.add(SatelliteRow(
                    id=satellite.id, planet_id=planet.id, orbital_period=satellite.orbitalPeriod,
                    creator=self.sponsor_id, created=now()))
        except IntegrityError:
            return self._refused(ResultCode.OBJECT_EXISTS, f"The satellite {satellite.id} exists", client_transaction_id)
        return self._ok(satellite, client_transaction_id)

    def replace(self, wanted: SatelliteReplacement, current=None, client_transaction_id=None):
        with self._context.database.transaction() as session:
            row = session.get(SatelliteRow, wanted.id)
            if row is None:
                return self._missing(wanted.id, client_transaction_id)
            planet = session.get(PlanetRow, row.planet_id)
            refusal = self._refusal(session, row, planet, "update", client_transaction_id)
            if refusal is not None:
                return refusal
            current = current or self._ok(to_satellite(row, planet), client_transaction_id)
            if row.orbital_period == wanted.orbitalPeriod:
                return ReplaceOutcome(current=current)
            row.orbital_period = wanted.orbitalPeriod
            row.updater, row.updated = self.sponsor_id, now()
        return ReplaceOutcome(current=current, update=wanted, mutation=self._ok(None, client_transaction_id))

    def delete(self, id, client_transaction_id=None):
        with self._context.database.transaction() as session:
            row = session.get(SatelliteRow, id)
            if row is None:
                return self._missing(id, client_transaction_id)
            refusal = self._refusal(session, row, session.get(PlanetRow, row.planet_id), "delete", client_transaction_id)
            if refusal is not None:
                return refusal
            session.delete(row)
        return self._ok(None, client_transaction_id)
