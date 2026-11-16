"""The common part of the SQLite demo backend: the password hashes, the clients, the database and its migrations."""
import pytest
from sqlalchemy import MetaData
from sqlalchemy.orm import Session

from core.result.error_response import ErrorResponse
from core.result.result_code import ResultCode
from registry_adapter.epp.gateways.epp_backend import EppBackend
from registry_adapter.rri.gateways.rri_backend import RriBackend
from registry_adapter.sqlite.client_directory import ClientDirectory
from registry_adapter.sqlite.common_part import COMMON_PART
from registry_adapter.sqlite.gateways.unsupported_gateway import UnsupportedGateway
from registry_adapter.sqlite.models.message_row import MessageRow
from registry_adapter.sqlite.password_hash import N, P, R, hash_password, verify_password
from registry_adapter.sqlite.schema_version_row import SchemaVersionRow
from registry_adapter.sqlite.sqlite_backend import SqliteBackend
from registry_adapter.sqlite.sqlite_database import SqliteDatabase
from registry_adapter.sqlite.sqlite_part import SqlitePart
from tests.helper.profiles import EPP_PROFILE, RRI_PROFILE, generic_profile


def test_a_hash_is_self_describing_and_salted():
    first, second = hash_password("pw", n=1024), hash_password("pw", n=1024)

    assert first.startswith("scrypt$1024$8$1$")
    assert first != second


def test_a_password_is_verified_against_its_hash():
    hashed = hash_password("right", n=1024)

    assert verify_password("right", hashed)
    assert not verify_password("wrong", hashed)


@pytest.mark.parametrize("stored", ["", "plain", "scrypt$x$8$1$AA==$AA==", "md5$1$1$1$AA==$AA==", "scrypt$1024$8$1$!!$!!",
                                    "scrypt$1024$8$1$AA==$AA==$extra"])
def test_a_malformed_hash_verifies_nothing(stored):
    assert not verify_password("anything", stored)


def test_clients_are_checked_by_user_and_password():
    clients = ClientDirectory({"demo": hash_password("pw", n=1024)})

    assert clients.verify("demo", "pw")
    assert not clients.verify("demo", "other")
    assert not clients.verify("ghost", "pw")


def test_the_tables_of_each_part_are_created_with_their_version():
    database = SqliteDatabase("sqlite://", [COMMON_PART])

    with database.transaction() as session:
        assert session.get(SchemaVersionRow, "common").version == 1
        session.add(MessageRow(client="a", created="t", text="x", object_type="planet", object_id="p", tr_status="pending",
                               request_date="t", action_date="t", requesting_client="b", acting_client="a"))
    with database.transaction() as session:
        assert session.get(MessageRow, 1).client == "a"


def test_a_database_of_another_schema_version_is_not_started(tmp_path):
    url = f"sqlite:///{tmp_path / 'demo.db'}"
    SqliteDatabase(url, [COMMON_PART]).close()
    newer = SqlitePart(name="common", version=2, metadata=MetaData())

    with pytest.raises(ValueError, match="schema version 1, and the code needs 2"):
        SqliteDatabase(url, [newer])


def test_a_database_file_keeps_its_data_over_a_restart(tmp_path):
    url = f"sqlite:///{tmp_path / 'demo.db'}"
    first = SqliteDatabase(url, [COMMON_PART])
    with first.transaction() as session:
        session.add(MessageRow(client="a", created="t", text="x", object_type="planet", object_id="p", tr_status="pending",
                               request_date="t", action_date="t", requesting_client="b", acting_client="a"))
    first.close()

    again = SqliteDatabase(url, [COMMON_PART])

    with again.transaction() as session:
        assert session.get(MessageRow, 1) is not None


def test_only_a_sqlite_url_is_taken():
    with pytest.raises(ValueError, match="sqlite URL"):
        SqliteDatabase("postgresql://localhost/x", [COMMON_PART])


def test_a_failed_unit_of_work_is_rolled_back():
    database = SqliteDatabase("sqlite://", [COMMON_PART])

    with pytest.raises(RuntimeError):
        with database.transaction() as session:
            session.add(MessageRow(client="a", created="t", text="x", object_type="planet", object_id="p",
                                   tr_status="pending", request_date="t", action_date="t", requesting_client="b",
                                   acting_client="a"))
            raise RuntimeError("fails")

    with Session(database.engine) as session:
        assert session.get(MessageRow, 1) is None


def test_a_gateway_of_an_object_the_backend_does_not_hold_refuses_every_command():
    gateway = UnsupportedGateway("contact")

    for answer in (gateway.info("c1", client_transaction_id="t"), gateway.transfer(object()), gateway.renew(object())):
        assert isinstance(answer, ErrorResponse)
        assert answer.code == ResultCode.UNIMPLEMENTED_OBJECT_SERVICE
    assert gateway.info("c1", client_transaction_id="t").client_transaction_id == "t"


def test_the_session_of_a_client_is_that_client():
    database = SqliteDatabase("sqlite://", [COMMON_PART])
    clients = ClientDirectory({"demo": hash_password("pw", n=1024)})
    profile = generic_profile("sqlite")

    good = SqliteBackend(database, clients, profile, [], "demo", "pw")
    bad = SqliteBackend(database, clients, profile, [], "demo", "wrong")

    assert good.connected and good.sponsor_id == "demo"
    assert good.verify_credentials("demo", "pw") and not good.verify_credentials("demo", "wrong")
    assert not good.verify_credentials("other", "pw")
    assert not bad.connected
    with pytest.raises(KeyError):
        good.extension("no.such.extension")


def test_the_protocol_backends_hold_no_extension():
    for backend in (EppBackend(object(), {}, EPP_PROFILE), RriBackend(object(), RRI_PROFILE)):
        with pytest.raises(KeyError):
            backend.extension("org.example.rpp.extension.planets")


def test_an_unknown_user_is_compared_with_the_highest_parameters_of_the_configured_hashes():
    clients = ClientDirectory({"a": hash_password("pw", n=1024, r=8, p=1), "b": hash_password("pw", n=2048, r=4, p=2)})

    assert clients.stand_in_parameters == (2048, 8, 2)
    assert not clients.verify("ghost", "pw")


def test_without_configured_hashes_the_stand_in_has_the_default_parameters():
    assert ClientDirectory({}).stand_in_parameters == (N, R, P)
