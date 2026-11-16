import hmac

from sqlalchemy.exc import IntegrityError

from core.model.message.transfer_event import TransferEvent
from core.model.shared.availability import Availability
from core.model.shared.contact_transfer_process import ContactTransferProcess
from core.model.shared.transfer_operation import TransferOperation
from core.result.result_code import ResultCode
from extensions.planets.core.model.planet import Planet
from extensions.planets.core.model.planet_changes import PlanetChanges
from extensions.planets.core.model.planet_replacement import PlanetReplacement
from extensions.planets.core.model.planet_rules import planet_violations
from extensions.planets.core.model.planet_transfer import PlanetTransfer
from registry_adapter.sqlite.clock import now
from registry_adapter.sqlite.extensions.planets.gateways.planet_rows import PENDING, is_pending, to_planet, transfer_of
from registry_adapter.sqlite.extensions.planets.models.planet_row import PlanetRow
from registry_adapter.sqlite.extensions.planets.models.planet_transfer_row import PlanetTransferRow
from registry_adapter.sqlite.extensions.planets.models.satellite_row import SatelliteRow
from registry_adapter.sqlite.gateways.refusal import Refusal
from registry_adapter.sqlite.gateways.sqlite_gateway import SqliteGateway

OBJECT_TYPE = "planet"

CLIENT_APPROVED = "clientApproved"
CLIENT_CANCELLED = "clientCancelled"
CLIENT_REJECTED = "clientRejected"


def _process(transfer: PlanetTransferRow) -> ContactTransferProcess:
    return ContactTransferProcess(
        id=transfer.planet_id, trStatus=transfer.status, reqClientId=transfer.requesting_client,
        requestDate=transfer.request_date, actClientId=transfer.acting_client, actionDate=transfer.action_date)


def _event(transfer: PlanetTransferRow) -> TransferEvent:
    return TransferEvent(objectType=OBJECT_TYPE, objectId=transfer.planet_id, trStatus=transfer.status,
                         requestDate=transfer.request_date, actionDate=transfer.action_date, process=_process(transfer))


class SqlitePlanetGateway(SqliteGateway):
    """The planets of the demo backend, in the database. The sponsor of a planet is the client that created it, or won it
    by a transfer; only the sponsor changes or deletes it, and the transfer is EPP's (RFC 5731 section 3.2.4): a pull
    that waits until the sponsor answers it, with no approval after a period."""

    @staticmethod
    def _missing(planet_id: str):
        return Refusal(ResultCode.OBJECT_DOES_NOT_EXIST, f"The planet {planet_id} does not exist")

    def _owned(self, session, planet_id: str, what: str) -> PlanetRow:
        """The planet, for its sponsor to change while no transfer is pending; a `Refusal` otherwise."""
        row = session.get(PlanetRow, planet_id)
        if row is None:
            raise self._missing(planet_id)
        if row.sponsor != self.sponsor_id:
            raise Refusal(ResultCode.AUTHORIZATION_ERROR, f"Only the sponsoring client can {what} the planet")
        if is_pending(session, planet_id):
            raise Refusal(ResultCode.OBJECT_STATUS_PROHIBITS_OPERATION, f"The planet {planet_id} has a pending transfer")
        return row

    @staticmethod
    def _check(row: PlanetRow) -> None:
        """The invariants of the planet as it is to be stored."""
        violations = planet_violations(row.type, row.radius, row.mass, row.auth_pw)
        if violations:
            raise Refusal(ResultCode.PARAMETER_VALUE_RANGE_ERROR, "; ".join(violations))

    def check(self, id, client_transaction_id=None):
        with self._context.database.transaction() as session:
            taken = session.get(PlanetRow, id) is not None
        return self._ok(Availability(name=id, available=not taken, reason="in use" if taken else None),
                        client_transaction_id)

    def info(self, id, client_transaction_id=None):
        def work():
            with self._context.database.transaction() as session:
                row = session.get(PlanetRow, id)
                if row is None:
                    raise self._missing(id)
                return self._ok(to_planet(session, row, self.sponsor_id, self._hooks_for("planet")), client_transaction_id)
        return self._guarded(client_transaction_id, work)

    def create(self, planet: Planet, client_transaction_id=None):
        def work():
            row = PlanetRow(
                id=planet.id, type=planet.type, radius=planet.radius, mass=planet.mass,
                auth_pw=planet.authInfo.pw if planet.authInfo else "", sponsor=self.sponsor_id, creator=self.sponsor_id,
                created=now())
            self._check(row)
            try:
                with self._context.database.transaction() as session:
                    session.add(row)
                    session.flush()
                    for extension_id, value in planet.extensions.items():
                        self._hook("planet", extension_id).create(session, planet.id, value)
            except IntegrityError:
                raise Refusal(ResultCode.OBJECT_EXISTS, f"The planet {planet.id} exists") from None
            return self._ok(planet, client_transaction_id)
        return self._guarded(client_transaction_id, work)

    def replace(self, replacement: PlanetReplacement, client_transaction_id=None):
        def work():
            with self._context.database.transaction() as session:
                row = self._owned(session, replacement.id, "update")
                row.type, row.radius, row.mass = replacement.type, replacement.radius, replacement.mass
                if replacement.authInfo is not None:
                    row.auth_pw = replacement.authInfo.pw or ""
                self._replace_members(session, "planet", row.id, replacement.extensions)
                self._check(row)
                row.updater, row.updated = self.sponsor_id, now()
            return self._ok(None, client_transaction_id)
        return self._guarded(client_transaction_id, work)

    def patch(self, id: str, changes: PlanetChanges, client_transaction_id=None):
        def work():
            with self._context.database.transaction() as session:
                row = self._owned(session, id, "update")
                if changes.type is not None:
                    row.type = changes.type
                if changes.radius is not None:
                    row.radius = changes.radius
                if changes.mass is not None:
                    row.mass = changes.mass
                if changes.authInfo is not None:
                    row.auth_pw = changes.authInfo.pw or ""
                if "radius" in changes.cleared:
                    row.radius = None
                if "mass" in changes.cleared:
                    row.mass = None
                for extension_id, value in changes.extensions.items():
                    self._hook("planet", extension_id).change(session, id, value)
                self._check(row)
                row.updater, row.updated = self.sponsor_id, now()
            return self._ok(None, client_transaction_id)
        return self._guarded(client_transaction_id, work)

    def delete(self, id, client_transaction_id=None):
        def work():
            with self._context.database.transaction() as session:
                row = self._owned(session, id, "delete")
                if session.query(SatelliteRow).filter(SatelliteRow.planet_id == id).count():
                    raise Refusal(ResultCode.OBJECT_ASSOCIATION_PROHIBITS_OPERATION, f"The planet {id} has satellites")
                for hook in self._hooks_for("planet").values():
                    hook.delete(session, id)
                transfer = transfer_of(session, id)
                if transfer is not None:
                    session.delete(transfer)
                session.delete(row)
            return self._ok(None, client_transaction_id)
        return self._guarded(client_transaction_id, work)

    def transfer(self, transfer: PlanetTransfer, client_transaction_id=None):
        with self._context.database.transaction() as session:
            row = session.get(PlanetRow, transfer.id)
            if row is None:
                return self._refused(ResultCode.OBJECT_DOES_NOT_EXIST, f"The planet {transfer.id} does not exist",
                                     client_transaction_id)
            latest = transfer_of(session, transfer.id)
            operation = transfer.operation
            if operation == TransferOperation.REQUEST:
                return self._request(session, row, latest, transfer, client_transaction_id)
            if operation == TransferOperation.QUERY:
                return self._query(row, latest, client_transaction_id)
            if latest is None or latest.status != PENDING:
                return self._refused(ResultCode.OBJECT_NOT_PENDING_TRANSFER,
                                     f"The planet {transfer.id} has no pending transfer", client_transaction_id)
            if operation == TransferOperation.CANCEL:
                if latest.requesting_client != self.sponsor_id:
                    return self._refused(ResultCode.AUTHORIZATION_ERROR,
                                         "Only the requesting client can cancel the transfer", client_transaction_id)
                return self._conclude(session, row, latest, CLIENT_CANCELLED, row.sponsor, client_transaction_id)
            if row.sponsor != self.sponsor_id:
                return self._refused(ResultCode.AUTHORIZATION_ERROR,
                                     "Only the sponsoring client can answer the transfer", client_transaction_id)
            status = CLIENT_APPROVED if operation == TransferOperation.APPROVE else CLIENT_REJECTED
            return self._conclude(session, row, latest, status, latest.requesting_client, client_transaction_id)

    def _request(self, session, row: PlanetRow, latest, transfer: PlanetTransfer, client_transaction_id):
        given = transfer.authInfo.pw if transfer.authInfo else None
        if not given or not hmac.compare_digest(given.encode("utf-8"), row.auth_pw.encode("utf-8")):
            return self._refused(ResultCode.INVALID_AUTHORIZATION_INFORMATION,
                                 "The authorisation information of the planet is not valid", client_transaction_id)
        if row.sponsor == self.sponsor_id:
            return self._refused(ResultCode.OBJECT_NOT_ELIGIBLE_FOR_TRANSFER,
                                 f"The planet {row.id} is sponsored by the requesting client", client_transaction_id)
        if latest is not None and latest.status == PENDING:
            return self._refused(ResultCode.OBJECT_PENDING_TRANSFER, f"The planet {row.id} has a pending transfer",
                                 client_transaction_id)
        if latest is not None:
            session.delete(latest)
            session.flush()
        requested = now()
        # No approval after a period: the action date of a pending transfer is the date of the request.
        latest = PlanetTransferRow(planet_id=row.id, status=PENDING, requesting_client=self.sponsor_id,
                                   request_date=requested, acting_client=row.sponsor, action_date=requested)
        session.add(latest)
        self._context.messages.add_transfer_event(
            session, row.sponsor, _event(latest), f"Transfer of the planet {row.id} requested by {self.sponsor_id}.")
        return self._ok(_process(latest), client_transaction_id, ResultCode.COMMAND_COMPLETED_ACTION_PENDING,
                        "Command completed successfully; action pending")

    def _query(self, row: PlanetRow, latest, client_transaction_id):
        if latest is None:
            return self._refused(ResultCode.OBJECT_NOT_PENDING_TRANSFER, f"The planet {row.id} has no transfer",
                                 client_transaction_id)
        if self.sponsor_id not in (row.sponsor, latest.requesting_client, latest.acting_client):
            return self._refused(ResultCode.AUTHORIZATION_ERROR, "Only a client of the transfer can query it",
                                 client_transaction_id)
        return self._ok(_process(latest), client_transaction_id)

    def _conclude(self, session, row: PlanetRow, latest, status: str, notified: str, client_transaction_id):
        """Ends the pending transfer with `status`, queues the message of the other client (`notified`), and, on approval,
        gives the planet to the requester: its satellites follow, as their sponsor is the planet's."""
        latest.status, latest.action_date = status, now()
        if status == CLIENT_APPROVED:
            latest.acting_client = self.sponsor_id
            row.sponsor, row.transferred = latest.requesting_client, latest.action_date
        else:
            latest.acting_client = row.sponsor
        self._context.messages.add_transfer_event(
            session, notified, _event(latest), f"Transfer of the planet {row.id}: {status}.")
        return self._ok(_process(latest), client_transaction_id)
