import pytest

from indexclient.mocks import MockIndexClient


@pytest.fixture
def mock_client():
    return MockIndexClient('http://localhost:8001', auth=('admin', 'admin'))


def test_instantiation(mock_client):
    assert mock_client


def test_create(mock_client):
    baseid = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    filename = 'key'
    urls = ['s3://url/bucket/' + filename]
    urls_metadata = {url: {'state': 'doing ok'} for url in urls}
    size = 5
    acl = ['a', 'b']
    hashes = {'md5': 'ab167e49d25b488939b1ede42752458b'}
    doc = mock_client.create(
        hashes=hashes,
        file_name=filename,
        size=size,
        urls=urls,
        acl=acl,
        baseid=baseid,
        urls_metadata=urls_metadata,
    )
    assert doc.size == 5
    assert doc.hashes == hashes
    assert doc.size == size
    assert doc.urls == urls
    assert doc.baseid == baseid
    assert doc.urls_metadata == urls_metadata
    assert doc.acl == acl
