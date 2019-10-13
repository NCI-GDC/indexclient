import json

from indexclient.client import Document, IndexClient
from indexclient.mocks.errors import UserError
from indexclient.mocks.mock_indexd import (
    create as mock_indexd_create,
    get as mock_indexd_get,
)


class MockResponse(object):

    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data


class MockIndexClient(IndexClient):

    def __init__(self, baseurl, version="v0", auth=None):
        self.store = {}
        super(MockIndexClient, self).__init__(baseurl, version, auth)

    def get(self, did):
        pass

    def add_version(self, current_did, new_doc):
        pass

    def check_status(self):
        pass

    def global_get(self, did, no_dist=False):
        pass

    def bulk_request(self, dids):
        pass

    def bulk_get_latest(self, dids, skip_null=False):
        pass

    def get_with_params(self, params=None):
        pass

    def list(self, limit=float("inf"), start=None, page_size=100):
        pass

    def list_with_params(self, limit=float("inf"), start=None, page_size=100, params=None, negate_params=None):
        pass

    def create(self, hashes, size, did=None, urls=None, file_name=None, metadata=None, baseid=None, acl=None,
               urls_metadata=None, version=None):

        if urls is None:
            urls = []

        data = {
            "urls": urls,
            "form": "object",
            "hashes": hashes,
            "size": size,
            "file_name": file_name,
            "metadata": metadata or {},
            "urls_metadata": urls_metadata,
            "baseid": baseid,
            "acl": acl,
            "version": version or ''
        }

        if did:
            data["did"] = did

        res = mock_indexd_create(self, data)

        return Document(self, res['did'])

    def create_alias(self, record, size, hashes, release=None, metastring=None, host_authorities=None,
                     keeper_authority=None):
        pass

    def get_latest_version(self, did, skip_null_versions=False):
        pass

    def list_versions(self, did):
        pass

    def _get(self, *path, **kwargs):
        if len(path) == 2 and path[0] == 'index':
            return MockResponse(mock_indexd_get(self, path[1]))
        raise UserError(
            'Unimplemented path {path} with kwargs {kwargs}'
            .format(path=path, kwargs=kwargs)
        )

    def _post(self, *path, **kwargs):
        pass

    def _put(self, *path, **kwargs):
        pass

    def _delete(self, *path, **kwargs):
        pass
