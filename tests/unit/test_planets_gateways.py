"""The planet and satellite gateways of the SQLite backend, below the wire: PUT and PATCH are native and atomic, nothing of
JSON reaches them, and an extension that adds members to a planet or a satellite takes part in the same unit of work, which
a dummy extension (its own table, typed core objects, a hook) shows."""
from dataclasses import dataclass
from typing import Optional

import pytest
from sqlalchemy import Column, Integer, MetaData, String, Table, delete, insert, select

from core.model.shared.common import AuthInfo
from core.model.shared.transfer_operation import TransferOperation
from core.result.error_response import ErrorResponse
from core.result.result_code import ResultCode
from extensions.planets.core.model.planet import Planet
from extensions.planets.core.model.planet_changes import PlanetChanges
from extensions.planets.core.model.planet_replacement import PlanetReplacement
from extensions.planets.core.model.planet_transfer import PlanetTransfer
from extensions.planets.core.model.satellite import Satellite
from extensions.planets.core.model.satellite_changes import SatelliteChanges
from extensions.planets.core.model.satellite_replacement import SatelliteReplacement
from extensions.planets.core.ports.planets_gateways import EXTENSION_ID
from registry_adapter.sqlite.client_directory import ClientDirectory
from registry_adapter.sqlite.common_part import COMMON_PART
from registry_adapter.sqlite.extension_part import ExtensionPart, load_extension_parts
from registry_adapter.sqlite.member_refused import MemberRefused
from registry_adapter.sqlite.password_hash import hash_password
from registry_adapter.sqlite.sqlite_backend import SqliteBackend
from registry_adapter.sqlite.sqlite_database import SqliteDatabase
from registry_adapter.sqlite.sqlite_part import SqlitePart
from tests.helper.profiles import generic_profile

DUMMY = "x.dummy.atmosphere"
PASSWORD = "Secret-Word1"

dummy_metadata = MetaData()
dummy_table = Table("dummy_members", dummy_metadata, Column("object_id", String, primary_key=True),
                    Column("pressure", Integer))


@dataclass(frozen=True)
class Pressure:
    """What the dummy extension adds to a planet and to a patch of one: a typed object of its own core."""
    pressure: Optional[int] = None


class PressureHook:
    """The SQLite part of the dummy extension: its table, in the unit of work of the planet."""

    def create(self, session, object_id, value):
        self._check(value)
        session.execute(insert(dummy_table).values(object_id=object_id, pressure=value.pressure))

    def replace(self, session, object_id, value):
        session.execute(delete(dummy_table).where(dummy_table.c.object_id == object_id))
        if value is not None:
            self.create(session, object_id, value)

    def change(self, session, object_id, changes):
        self._check(changes)
        session.execute(delete(dummy_table).where(dummy_table.c.object_id == object_id))
        session.execute(insert(dummy_table).values(object_id=object_id, pressure=changes.pressure))

    def read(self, session, object_id):
        row = session.execute(select(dummy_table.c.pressure).where(dummy_table.c.object_id == object_id)).first()
        return None if row is None else Pressure(pressure=row[0])

    def delete(self, session, object_id):
        session.execute(delete(dummy_table).where(dummy_table.c.object_id == object_id))

    @staticmethod
    def _check(value):
        if value.pressure is not None and value.pressure < 0:
            raise MemberRefused("The pressure of a planet is not negative")


@pytest.fixture
def backends():
    """The backends of two clients over one database with the planets part and the dummy extension's."""
    parts = load_extension_parts({EXTENSION_ID: "registry_adapter.sqlite.extensions.planets"})
    parts.append(ExtensionPart(extension_id=DUMMY, part=SqlitePart("dummy", 1, dummy_metadata),
                               hooks={"planet": PressureHook()}))
    database = SqliteDatabase("sqlite://", [COMMON_PART, *(part.part for part in parts)])
    clients = ClientDirectory({"a": hash_password("pw", n=1024), "b": hash_password("pw", n=1024)})
    profile = generic_profile("sqlite")
    made = {who: SqliteBackend(database, clients, profile, parts, who, "pw").extension(EXTENSION_ID) for who in "ab"}
    yield made
    database.close()


def planet(name="mars", **members):
    return Planet(id=name, type="rocky", radius=3389.5, mass=0.1, authInfo=AuthInfo(pw=PASSWORD), **members)


def ok(answer):
    assert not isinstance(answer, ErrorResponse), answer
    return answer


def refused(answer, code):
    assert isinstance(answer, ErrorResponse) and answer.code == code, answer


def test_a_planet_is_replaced_natively(backends):
    planets = backends["a"].planets
    ok(planets.create(planet()))

    ok(planets.replace(PlanetReplacement(id="mars", type="gas-giant", radius=5.0)))

    stored = ok(planets.info("mars")).payload
    assert (stored.type, stored.radius, stored.mass) == ("gas-giant", 5.0, None)
    assert stored.authInfo.pw == PASSWORD  # without authInfo the planet keeps its own
    assert stored.upID == "a"


def test_a_planet_is_patched_natively(backends):
    planets = backends["a"].planets
    ok(planets.create(planet()))

    ok(planets.patch("mars", PlanetChanges(radius=7.0, cleared=frozenset({"mass"}), authInfo=AuthInfo(pw="New-Word2"))))

    stored = ok(planets.info("mars")).payload
    assert (stored.type, stored.radius, stored.mass, stored.authInfo.pw) == ("rocky", 7.0, None, "New-Word2")


def test_a_replace_or_patch_of_an_unknown_planet_is_not_found(backends):
    planets = backends["a"].planets

    refused(planets.replace(PlanetReplacement(id="nowhere", type="rocky")), ResultCode.OBJECT_DOES_NOT_EXIST)
    refused(planets.patch("nowhere", PlanetChanges(radius=1.0)), ResultCode.OBJECT_DOES_NOT_EXIST)


def test_only_the_sponsor_replaces_or_patches_and_nothing_is_written_otherwise(backends):
    ok(backends["a"].planets.create(planet()))

    refused(backends["b"].planets.replace(PlanetReplacement(id="mars", type="ice-giant")), ResultCode.AUTHORIZATION_ERROR)
    refused(backends["b"].planets.patch("mars", PlanetChanges(type="ice-giant")), ResultCode.AUTHORIZATION_ERROR)

    stored = ok(backends["a"].planets.info("mars")).payload
    assert (stored.type, stored.upDate) == ("rocky", None)


def test_a_pending_transfer_prohibits_a_replace_or_a_patch(backends):
    ok(backends["a"].planets.create(planet()))
    ok(backends["b"].planets.transfer(PlanetTransfer(id="mars", operation=TransferOperation.REQUEST,
                                                    authInfo=AuthInfo(pw=PASSWORD))))

    refused(backends["a"].planets.replace(PlanetReplacement(id="mars", type="ice-giant")),
            ResultCode.OBJECT_STATUS_PROHIBITS_OPERATION)
    refused(backends["a"].planets.patch("mars", PlanetChanges(type="ice-giant")),
            ResultCode.OBJECT_STATUS_PROHIBITS_OPERATION)


@pytest.mark.parametrize("changes", [PlanetChanges(type="moonlike"), PlanetChanges(radius=-1.0), PlanetChanges(mass=0.0),
                                     PlanetChanges(authInfo=AuthInfo(pw=""))])
def test_a_patch_whose_result_breaks_an_invariant_is_refused_and_not_stored(backends, changes):
    planets = backends["a"].planets
    ok(planets.create(planet()))

    refused(planets.patch("mars", PlanetChanges(type=changes.type, radius=changes.radius, mass=changes.mass,
                                                authInfo=changes.authInfo)), ResultCode.PARAMETER_VALUE_RANGE_ERROR)

    stored = ok(planets.info("mars")).payload
    assert (stored.type, stored.radius, stored.mass, stored.authInfo.pw) == ("rocky", 3389.5, 0.1, PASSWORD)


def test_a_replace_whose_result_breaks_an_invariant_is_refused(backends):
    refused_ = backends["a"].planets
    ok(refused_.create(planet()))

    refused(refused_.replace(PlanetReplacement(id="mars", type="moonlike")), ResultCode.PARAMETER_VALUE_RANGE_ERROR)

    assert ok(refused_.info("mars")).payload.type == "rocky"


def test_a_satellite_is_replaced_and_patched_natively(backends):
    ok(backends["a"].planets.create(planet()))
    satellites = backends["a"].satellites
    ok(satellites.create(Satellite(id="phobos", planet="mars", orbitalPeriod=0.3)))

    ok(satellites.replace(SatelliteReplacement(id="phobos", orbitalPeriod=1.0)))
    assert ok(satellites.info("phobos")).payload.orbitalPeriod == 1.0
    ok(satellites.patch("phobos", SatelliteChanges(cleared=frozenset({"orbitalPeriod"}))))
    assert ok(satellites.info("phobos")).payload.orbitalPeriod is None
    refused(satellites.patch("phobos", SatelliteChanges(orbitalPeriod=-3.0)), ResultCode.PARAMETER_VALUE_RANGE_ERROR)
    refused(backends["b"].satellites.patch("phobos", SatelliteChanges(orbitalPeriod=3.0)), ResultCode.AUTHORIZATION_ERROR)
    refused(backends["a"].satellites.patch("nowhere", SatelliteChanges(orbitalPeriod=3.0)),
            ResultCode.OBJECT_DOES_NOT_EXIST)


def test_a_satellite_cannot_change_while_its_planet_has_a_pending_transfer(backends):
    ok(backends["a"].planets.create(planet()))
    ok(backends["a"].satellites.create(Satellite(id="phobos", planet="mars", orbitalPeriod=0.3)))
    ok(backends["b"].planets.transfer(PlanetTransfer(id="mars", operation=TransferOperation.REQUEST,
                                                    authInfo=AuthInfo(pw=PASSWORD))))

    refused(backends["a"].satellites.patch("phobos", SatelliteChanges(orbitalPeriod=3.0)),
            ResultCode.OBJECT_STATUS_PROHIBITS_OPERATION)
    refused(backends["a"].satellites.replace(SatelliteReplacement(id="phobos", orbitalPeriod=3.0)),
            ResultCode.OBJECT_STATUS_PROHIBITS_OPERATION)


# --- an extension that adds members to a planet

def test_an_extension_adds_members_to_a_planet_end_to_end(backends):
    planets = backends["a"].planets
    ok(planets.create(planet(extensions={DUMMY: Pressure(pressure=90)})))
    assert ok(planets.info("mars")).payload.extensions == {DUMMY: Pressure(pressure=90)}

    ok(planets.patch("mars", PlanetChanges(extensions={DUMMY: Pressure(pressure=1)})))
    assert ok(planets.info("mars")).payload.extensions == {DUMMY: Pressure(pressure=1)}

    ok(planets.replace(PlanetReplacement(id="mars", type="rocky", extensions={DUMMY: Pressure(pressure=5)})))
    assert ok(planets.info("mars")).payload.extensions == {DUMMY: Pressure(pressure=5)}

    ok(planets.replace(PlanetReplacement(id="mars", type="rocky")))  # a full update without the member removes it
    assert ok(planets.info("mars")).payload.extensions == {}


def test_a_planet_without_the_members_of_an_extension_has_none(backends):
    ok(backends["a"].planets.create(planet()))

    assert ok(backends["a"].planets.info("mars")).payload.extensions == {}


def test_a_hook_that_refuses_rolls_the_whole_patch_back(backends):
    planets = backends["a"].planets
    ok(planets.create(planet(extensions={DUMMY: Pressure(pressure=90)})))

    refused(planets.patch("mars", PlanetChanges(type="ice-giant", extensions={DUMMY: Pressure(pressure=-1)})),
            ResultCode.PARAMETER_VALUE_RANGE_ERROR)

    stored = ok(planets.info("mars")).payload
    assert (stored.type, stored.extensions) == ("rocky", {DUMMY: Pressure(pressure=90)})


def test_a_core_invariant_rolls_the_hook_back_too(backends):
    planets = backends["a"].planets
    ok(planets.create(planet(extensions={DUMMY: Pressure(pressure=90)})))

    refused(planets.patch("mars", PlanetChanges(radius=-1.0, extensions={DUMMY: Pressure(pressure=7)})),
            ResultCode.PARAMETER_VALUE_RANGE_ERROR)

    assert ok(planets.info("mars")).payload.extensions == {DUMMY: Pressure(pressure=90)}


def test_a_create_that_a_hook_refuses_stores_nothing(backends):
    planets = backends["a"].planets

    refused(planets.create(planet(extensions={DUMMY: Pressure(pressure=-1)})), ResultCode.PARAMETER_VALUE_RANGE_ERROR)

    refused(planets.info("mars"), ResultCode.OBJECT_DOES_NOT_EXIST)


def test_members_of_an_extension_the_backend_does_not_hold_are_refused(backends):
    planets = backends["a"].planets
    ok(planets.create(planet()))

    refused(planets.patch("mars", PlanetChanges(type="ice-giant", extensions={"x.unknown": object()})),
            ResultCode.UNIMPLEMENTED_EXTENSION)
    refused(planets.replace(PlanetReplacement(id="mars", type="ice-giant", extensions={"x.unknown": object()})),
            ResultCode.UNIMPLEMENTED_EXTENSION)
    refused(planets.create(planet("venus", extensions={"x.unknown": object()})), ResultCode.UNIMPLEMENTED_EXTENSION)

    assert ok(planets.info("mars")).payload.type == "rocky"
    refused(planets.info("venus"), ResultCode.OBJECT_DOES_NOT_EXIST)


def test_a_hook_is_called_in_the_unit_of_the_sponsor_check(backends):
    ok(backends["a"].planets.create(planet(extensions={DUMMY: Pressure(pressure=90)})))

    refused(backends["b"].planets.patch("mars", PlanetChanges(extensions={DUMMY: Pressure(pressure=1)})),
            ResultCode.AUTHORIZATION_ERROR)

    assert ok(backends["a"].planets.info("mars")).payload.extensions == {DUMMY: Pressure(pressure=90)}


def test_deleting_a_planet_deletes_what_the_extension_holds(backends):
    planets = backends["a"].planets
    ok(planets.create(planet(extensions={DUMMY: Pressure(pressure=90)})))

    ok(planets.delete("mars"))

    ok(planets.create(planet()))
    assert ok(planets.info("mars")).payload.extensions == {}


def test_what_the_gateways_take_holds_no_json():
    """The change sets and the replacements are typed core objects: no member is a dict of JSON or a JSON Pointer."""
    for kind in (PlanetChanges, SatelliteChanges, PlanetReplacement, SatelliteReplacement):
        annotations = " ".join(str(annotation) for annotation in kind.__annotations__.values())
        assert "dict" not in annotations and "list" not in annotations
