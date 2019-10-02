import pytest

from indexclient.mock import MockIndexClient


@pytest.fixture
def mock_client():
    return MockIndexClient('http://localhost:8001', auth=('admin', 'admin'))


def test_instantiation(mock_client):
    assert mock_client
