from sqlalchemy.exc import IntegrityError

from core.model.shared.availability import Availability
from core.result.result_code import ResultCode
from extensions.planets.core.model.satellite import Satellite
from extensions.planets.core.model.planet_rules import satellite_violations
from extensions.planets.core.model.satellite_changes import SatelliteChanges
from extensions.planets.core.model.satellite_replacement import SatelliteReplacement
from registry_adapter.sqlite.clock import now
from registry_adapter.sqlite.extensions.planets.gateways.planet_rows import is_pending, to_satellite
from registry_adapter.sqlite.extensions.planets.models.planet_row import PlanetRow
from registry_adapter.sqlite.extensions.planets.models.satellite_row import SatelliteRow
from registry_adapter.sqlite.gateways.refusal import Refusal
from registry_adapter.sqlite.gateways.sqlite_gateway import SqliteGateway


class SqliteSatelliteGateway(SqliteGateway):
    """The satellites of the demo backend. The sponsor of a satellite is that of its planet."""

    @property
    def _hooks(self):
        return self._context.hooks.get("satellite", {})

    @staticmethod
    def _missing(satellite_id: str):
        return Refusal(ResultCode.OBJECT_DOES_NOT_EXIST, f"The satellite {satellite_id} does not exist")

    def _owned(self, session, satellite_id: str, what: str):
        """The satellite and its planet, for the sponsor of the planet to change while no transfer of it is pending; a
        `Refusal` otherwise."""
        row = session.get(SatelliteRow, satellite_id)
        if row is None:
            raise self._missing(satellite_id)
        planet = session.get(PlanetRow, row.planet_id)
        if planet.sponsor != self.sponsor_id:
            raise Refusal(ResultCode.AUTHORIZATION_ERROR, f"Only the sponsoring client can {what} the satellite")
        if is_pending(session, planet.id):
            raise Refusal(ResultCode.OBJECT_STATUS_PROHIBITS_OPERATION,
                          f"The planet {planet.id} of the satellite has a pending transfer")
        return row

    @staticmethod
    def _check(orbital_period) -> None:
        violations = satellite_violations(orbital_period)
        if violations:
            raise Refusal(ResultCode.PARAMETER_VALUE_RANGE_ERROR, "; ".join(violations))

    def _hook(self, extension_id: str):
        hook = self._hooks.get(extension_id)
        if hook is None:
            raise Refusal(ResultCode.UNIMPLEMENTED_EXTENSION, f"The backend holds no members of {extension_id}")
        return hook

    def check(self, id, client_transaction_id=None):
        with self._context.database.transaction() as session:
            taken = session.get(SatelliteRow, id) is not None
        return self._ok(Availability(name=id, available=not taken, reason="in use" if taken else None),
                        client_transaction_id)

    def info(self, id, client_transaction_id=None):
        def work():
            with self._context.database.transaction() as session:
                row = session.get(SatelliteRow, id)
                if row is None:
                    raise self._missing(id)
                return self._ok(to_satellite(session, row, session.get(PlanetRow, row.planet_id), self._hooks),
                                client_transaction_id)
        return self._guarded(client_transaction_id, work)

    def create(self, satellite: Satellite, client_transaction_id=None):
        def work():
            self._check(satellite.orbitalPeriod)
            try:
                with self._context.database.transaction() as session:
                    planet = session.get(PlanetRow, satellite.planet)
                    if planet is None:
                        raise Refusal(ResultCode.OBJECT_DOES_NOT_EXIST, f"The planet {satellite.planet} does not exist")
                    if planet.sponsor != self.sponsor_id:
                        raise Refusal(ResultCode.AUTHORIZATION_ERROR,
                                      f"Only the sponsoring client of the planet {planet.id} can create its satellite")
                    session.add(SatelliteRow(
                        id=satellite.id, planet_id=planet.id, orbital_period=satellite.orbitalPeriod,
                        creator=self.sponsor_id, created=now()))
                    session.flush()
                    for extension_id, value in satellite.extensions.items():
                        self._hook(extension_id).create(session, satellite.id, value)
            except IntegrityError:
                raise Refusal(ResultCode.OBJECT_EXISTS, f"The satellite {satellite.id} exists") from None
            return self._ok(satellite, client_transaction_id)
        return self._guarded(client_transaction_id, work)

    def replace(self, replacement: SatelliteReplacement, client_transaction_id=None):
        def work():
            with self._context.database.transaction() as session:
                row = self._owned(session, replacement.id, "update")
                row.orbital_period = replacement.orbitalPeriod
                for extension_id in replacement.extensions.keys() - self._hooks.keys():
                    self._hook(extension_id)
                for extension_id, hook in self._hooks.items():
                    hook.replace(session, row.id, replacement.extensions.get(extension_id))
                self._check(row.orbital_period)
                row.updater, row.updated = self.sponsor_id, now()
            return self._ok(None, client_transaction_id)
        return self._guarded(client_transaction_id, work)

    def patch(self, id: str, changes: SatelliteChanges, client_transaction_id=None):
        def work():
            with self._context.database.transaction() as session:
                row = self._owned(session, id, "update")
                if changes.orbitalPeriod is not None:
                    row.orbital_period = changes.orbitalPeriod
                if "orbitalPeriod" in changes.cleared:
                    row.orbital_period = None
                for extension_id, value in changes.extensions.items():
                    self._hook(extension_id).change(session, id, value)
                self._check(row.orbital_period)
                row.updater, row.updated = self.sponsor_id, now()
            return self._ok(None, client_transaction_id)
        return self._guarded(client_transaction_id, work)

    def delete(self, id, client_transaction_id=None):
        def work():
            with self._context.database.transaction() as session:
                row = self._owned(session, id, "delete")
                for hook in self._hooks.values():
                    hook.delete(session, id)
                session.delete(row)
            return self._ok(None, client_transaction_id)
        return self._guarded(client_transaction_id, work)
