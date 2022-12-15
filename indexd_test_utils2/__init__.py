import hashlib
import os
import random
import socket
import threading
import uuid
from typing import Dict, Optional, Tuple

import flask
import pytest
import requests
from indexd import app_init
from indexd.alias.drivers.alchemy import Base as AliasBase
from indexd.alias.drivers.alchemy import SQLAlchemyAliasDriver
from indexd.auth.drivers.alchemy import SQLAlchemyAuthDriver
from indexd.index.drivers.alchemy import Base as IndexBase
from indexd.index.drivers.alchemy import IndexDriverABC, SQLAlchemyIndexDriver
from pytest_postgresql import factories
from pytest_postgresql.executor import PostgreSQLExecutor

from indexclient.client import Document, IndexClient
from indexd_test_utils2 import indexd_settings

INDEXD_DBNAME = os.getenv("INDEXD_DBNAME", "indexd_test")

postgresql_proc_indexd = factories.postgresql_proc(dbname=INDEXD_DBNAME)


@pytest.fixture(scope="session")
def pg_url(postgresql_proc_indexd: PostgreSQLExecutor) -> str:
    user = postgresql_proc_indexd.user
    password = postgresql_proc_indexd.password
    host = postgresql_proc_indexd.host
    port = postgresql_proc_indexd.port
    dbname = postgresql_proc_indexd.dbname
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


@pytest.fixture
def indexd_client(
    indexd_server: IndexDriverABC,
    create_indexd_tables: IndexDriverABC,
    indexd_admin_user: IndexDriverABC,
) -> IndexClient:
    """Create the tables and add an auth user"""
    return IndexClient(
        indexd_server.baseurl, auth=(indexd_admin_user[0], indexd_admin_user[1])
    )


class MockServer:
    def __init__(self, host: str, port: str):
        self.host = host
        self.port = port
        self.baseurl = f"http://{host}:{port}"


@pytest.fixture(scope="session")
def indexd_server(pg_url: str) -> MockServer:
    """
    Starts the indexd server, and cleans up its mess.
    Most tests will use the client which stems from this
    server fixture.

    Runs once per test session.
    """
    app = flask.Flask("indexd")
    # the side effect of the following line creates the db and tables.
    settings = indexd_settings.get_settings(pg_url)
    app_init(app, settings)

    host = os.getenv("INDEXD_HOST") or "localhost"

    debug = False
    port = random.randint(8000, 9000)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        while sock.connect_ex((host, port)) == 0:
            port = random.randint(8000, 9000)

    t = threading.Thread(
        target=app.run, kwargs={"host": host, "port": port, "debug": debug}
    )
    t.setDaemon(True)
    t.start()

    wait_for_indexd_alive(host, port)
    yield MockServer(host=host, port=port)


def wait_for_indexd_alive(host, port):
    url = f"http://{host}:{port}"
    try:
        requests.get(url)
    except requests.ConnectionError:
        return wait_for_indexd_alive(host, port)
    else:
        return


def create_random_index(
    index_client: IndexClient,
    did: Optional[str] = None,
    version: Optional[str] = None,
    hashes: Optional[Dict[str, str]] = None,
) -> Document:
    """
    Shorthand for creating new index entries for test purposes.
    Note:
        Expects index client v1.5.2 and above
    Args:
        index_client (indexclient.client.IndexClient): pytest fixture for index_client
        passed from actual test functions
        did (str): if specified it will be used as document did, else allows indexd to create one
        version (str): version of the index being added
        hashes (dict): hashes to store on the index, if not specified a random one is created
    Returns:
        indexclient.client.Document: the document just created
    """

    did = str(uuid.uuid4()) if did is None else did

    if not hashes:
        md5_hasher = hashlib.md5()
        md5_hasher.update(did.encode("utf-8"))
        hashes = {"md5": md5_hasher.hexdigest()}

    doc = index_client.create(
        did=did,
        hashes=hashes,
        size=random.randint(10, 1000),
        version=version,
        acl=["a", "b"],
        file_name=f"{did}_warning_huge_file.svs",
        urls=[f"s3://super-safe.com/{did}_warning_huge_file.svs"],
        urls_metadata={f"s3://super-safe.com/{did}_warning_huge_file.svs": {"a": "b"}},
    )

    return doc


def create_random_index_version(
    index_client: IndexClient,
    did: str,
    version_did: Optional[str] = None,
    version: Optional[str] = None,
) -> Document:
    """
    Shorthand for creating a dummy version of an existing index, use wisely as it does not assume any versioning
    scheme and null versions are allowed
    Args:
        index_client (IndexClient): pytest fixture for index_client
        passed from actual test functions
        did (str): existing member did
        version_did (str): did for the version to be created
        version (str): version number for the version to be created
    Returns:
        Document: the document just created
    """
    md5_hasher = hashlib.md5()
    md5_hasher.update(did.encode("utf-8"))
    file_name = did

    data = {}
    if version_did:
        data["did"] = version_did
        file_name = version_did
        md5_hasher.update(version_did.encode("utf-8"))

    data["acl"] = ["ax", "bx"]
    data["size"] = random.randint(10, 1000)
    data["hashes"] = {"md5": md5_hasher.hexdigest()}
    data["urls"] = [f"s3://super-safe.com/{file_name}_warning_huge_file.svs"]
    data["form"] = "object"
    data["file_name"] = f"{file_name}_warning_huge_file.svs"
    data["urls_metadata"] = {
        f"s3://super-safe.com/{file_name}_warning_huge_file.svs": {"a": "b"}
    }

    if version:
        data["version"] = version

    return index_client.add_version(did, Document(None, None, data))
