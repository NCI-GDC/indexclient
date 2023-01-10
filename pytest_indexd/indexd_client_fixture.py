import pytest
from indexd.index.driver import IndexDriverABC

from indexclient.client import IndexClient


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
