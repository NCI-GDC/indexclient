"""Module for indexd_client fixture

The index_client fixture is the fixture user should use most. This fixture will create
provide a working indexclient. The indexclient will talk to a test indexd server and
data will be saved to temporary postgres db.
"""
from typing import Tuple

import pytest
from _pytest.fixtures import fixture

from indexclient.client import IndexClient
from pytest_indexd.fixtures.server_fixture import MockServer


@pytest.fixture
def indexd_client(
    indexd_server: MockServer,
    create_indexd_tables: fixture,  # usefixtures will cause failure for this one
    indexd_admin_user: Tuple[str, str],
) -> IndexClient:
    """Create the tables and add an auth user"""
    return IndexClient(
        indexd_server.baseurl, auth=(indexd_admin_user[0], indexd_admin_user[1])
    )
