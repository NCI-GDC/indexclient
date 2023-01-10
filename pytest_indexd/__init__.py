import os
from typing import Tuple

import pytest
from indexd.alias.drivers.alchemy import Base as AliasBase
from indexd.alias.drivers.alchemy import SQLAlchemyAliasDriver
from indexd.auth.drivers.alchemy import SQLAlchemyAuthDriver
from indexd.index.drivers.alchemy import Base as IndexBase
from indexd.index.drivers.alchemy import IndexDriverABC, SQLAlchemyIndexDriver
from pytest_postgresql import factories
from pytest_postgresql.executor import PostgreSQLExecutor

from pytest_indexd import indexd_settings

INDEXD_DBNAME = os.getenv("INDEXD_DBNAME", "indexd_test")

if os.getenv("USE_RUNNING_PG", "true").lower() == "true":
    postgresql_server_indexd = factories.postgresql_noproc(
        host=os.getenv("PG_INDEXD_HOST", "localhost"),
        user=os.getenv("PG_INDEXD_USER", "postgres"),
        password=os.getenv("PG_INDEXD_PASS", ""),
        dbname=os.getenv("PG_INDEXD_NAME", "indexd_test"),
    )
else:
    postgresql_server_indexd = factories.postgresql_proc(dbname=INDEXD_DBNAME)


@pytest.fixture(scope="session")
def pg_url(postgresql_server_indexd: PostgreSQLExecutor) -> str:
    user = postgresql_server_indexd.user
    password = postgresql_server_indexd.password
    host = postgresql_server_indexd.host
    port = postgresql_server_indexd.port
    dbname = postgresql_server_indexd.dbname
    yield f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


def truncate_tables(driver: IndexDriverABC, base) -> None:
    """Drop all the tables in this application's scope.

    This has the same effect as deleting the sqlite file. Your test will have a
    fresh database for it's run.

    Drop tables in reverse order to avoid cascade drop errors.
    metadata is a sqlalchemy property.
    sorted_tables is a list of tables sorted by their dependencies.
    """
    with driver.engine.begin() as txn:
        for table in reversed(base.metadata.sorted_tables):
            # do not clear schema versions so each test does not re-trigger migration.
            if table.name not in ["index_schema_version", "alias_schema_version"]:
                txn.execute(f"TRUNCATE {table.name} CASCADE;")


@pytest.fixture
def index_driver(pg_url: str) -> IndexDriverABC:
    driver = SQLAlchemyIndexDriver(pg_url, auto_migrate=False)
    yield driver
    truncate_tables(driver, IndexBase)
    driver.dispose()


@pytest.fixture
def alias_driver(pg_url: str) -> IndexDriverABC:
    driver = SQLAlchemyAliasDriver(pg_url, auto_migrate=False)
    yield driver
    truncate_tables(driver, AliasBase)
    driver.dispose()


@pytest.fixture(scope="session")
def auth_driver(pg_url: str) -> IndexDriverABC:
    driver = SQLAlchemyAuthDriver(pg_url)
    yield driver
    driver.dispose()


@pytest.fixture
def indexd_admin_user(auth_driver: IndexDriverABC) -> Tuple[str, str]:
    username = password = "admin"
    auth_driver.add(username, password)
    yield username, password
    auth_driver.delete("admin")


@pytest.fixture
def index_driver_no_migrate(pg_url: str) -> IndexDriverABC:
    """
    This fixture is designed for testing migration scripts and can be used for
    any other situation where a migration is not desired on instantiation.
    """
    driver = SQLAlchemyIndexDriver(pg_url, auto_migrate=False)
    yield driver
    truncate_tables(driver, IndexBase)
    driver.dispose()


@pytest.fixture
def alias_driver_no_migrate(pg_url: str) -> IndexDriverABC:
    """
    This fixture is designed for testing migration scripts and can be used for
    any other situation where a migration is not desired on instantiation.
    """
    driver = SQLAlchemyAliasDriver(pg_url, auto_migrate=False)
    yield driver
    truncate_tables(driver, AliasBase)
    driver.dispose()


@pytest.fixture
def create_indexd_tables(
    index_driver: IndexDriverABC,
    alias_driver: IndexDriverABC,
    auth_driver: IndexDriverABC,
) -> None:
    """Make sure the tables are created but don't operate on them directly.
    Also set up the password to be accessed by the client tests.
    Migration not required as tables will be created with most recent models
    """
    pass


@pytest.fixture
def create_indexd_tables_no_migrate(
    index_driver_no_migrate: IndexDriverABC,
    alias_driver_no_migrate: IndexDriverABC,
    auth_driver: IndexDriverABC,
) -> None:
    """Make sure the tables are created but don't operate on them directly.

    There is no migration required for the SQLAlchemyAuthDriver.
    Also set up the password to be accessed by the client tests.
    """
    pass
