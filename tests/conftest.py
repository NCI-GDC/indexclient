import hashlib
import pytest
import random
import uuid

from indexclient.client import IndexClient
from indexd_test_utils import (
    alias_driver,
    auth_driver,
    create_indexd_tables,
    index_driver,
    indexd_server,
    setup_indexd_test_database,
)


@pytest.fixture
def index_client(indexd_server, create_indexd_tables):
    """Create the tables and add an auth user"""
    return IndexClient('http://localhost:8001', auth=('admin', 'admin'))
