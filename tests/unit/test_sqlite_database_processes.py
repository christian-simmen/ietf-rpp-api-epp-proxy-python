"""The SQLite demo database shared by the worker processes of one instance (#184): every uvicorn worker opens the same
file, creates the tables when it starts, and writes to it."""
import multiprocessing

from sqlalchemy import Column, Integer, MetaData, Table, select, text, update

from registry_adapter.sqlite.common_part import COMMON_PART
from registry_adapter.sqlite.schema_version_row import SchemaVersionRow
from registry_adapter.sqlite.sqlite_database import SqliteDatabase
from registry_adapter.sqlite.sqlite_part import SqlitePart

PROCESSES = 6
INCREMENTS = 25

COUNTER_METADATA = MetaData()
COUNTER = Table("counter", COUNTER_METADATA, Column("id", Integer, primary_key=True), Column("value", Integer))
COUNTER_PART = SqlitePart(name="counter", version=1, metadata=COUNTER_METADATA)
PARTS = [COMMON_PART, COUNTER_PART]


def _start(url: str, barrier) -> None:
    barrier.wait()
    SqliteDatabase(url, PARTS).close()


def _increment(url: str, barrier) -> None:
    database = SqliteDatabase(url, PARTS)
    barrier.wait()
    for _ in range(INCREMENTS):
        with database.transaction() as session:
            value = session.execute(select(COUNTER.c.value).where(COUNTER.c.id == 1)).scalar_one()
            session.execute(update(COUNTER).where(COUNTER.c.id == 1).values(value=value + 1))
    database.close()


def _run_together(target, url: str) -> list[int]:
    """Runs `target(url, barrier)` in PROCESSES processes released at once, and gives their exit codes."""
    context = multiprocessing.get_context("spawn")
    barrier = context.Barrier(PROCESSES)
    processes = [context.Process(target=target, args=(url, barrier)) for _ in range(PROCESSES)]
    for process in processes:
        process.start()
    for process in processes:
        process.join(timeout=120)
    return [process.exitcode for process in processes]


def test_a_database_file_is_written_ahead_so_that_readers_do_not_block_the_writer(tmp_path):
    database = SqliteDatabase(f"sqlite:///{tmp_path / 'demo.db'}", PARTS)

    with database.engine.connect() as connection:
        assert connection.execute(text("PRAGMA journal_mode")).scalar_one() == "wal"


def test_workers_starting_together_on_a_new_file_all_start_and_record_each_part_once(tmp_path):
    url = f"sqlite:///{tmp_path / 'demo.db'}"

    assert _run_together(_start, url) == [0] * PROCESSES

    database = SqliteDatabase(url, PARTS)
    with database.transaction() as session:
        assert sorted(row.part for row in session.scalars(select(SchemaVersionRow))) == ["common", "counter"]


def test_read_then_write_units_of_work_of_several_processes_lose_no_update(tmp_path):
    url = f"sqlite:///{tmp_path / 'demo.db'}"
    database = SqliteDatabase(url, PARTS)
    with database.transaction() as session:
        session.execute(COUNTER.insert().values(id=1, value=0))

    assert _run_together(_increment, url) == [0] * PROCESSES

    with database.transaction() as session:
        assert session.execute(select(COUNTER.c.value)).scalar_one() == PROCESSES * INCREMENTS
