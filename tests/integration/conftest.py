import os

import pytest

if os.getenv("USE_PYTEST_INDEXD", "false").lower() == "false":
    from indexd_test_utils import (
        alias_driver,
        auth_driver,
        create_indexd_tables,
        index_driver,
        indexd_admin_user,
        indexd_client,
        indexd_server,
        setup_indexd_test_database,
    )
else:
    # This only works in top level conftest
    pytest_plugins = ("pytest_indexd.plugin",)


from indexclient import client


@pytest.fixture(scope="function")
def index_client(indexd_client):
    """
    Handles getting all the docs from an
    indexing endpoint. Currently this is changing from
    signpost to indexd, so we'll use just indexd_client now.
    I.E. test to a common interface this could be multiply our
    tests:
    https://docs.pytest.org/en/latest/fixture.html#parametrizing-fixtures
    """
    return indexd_client
