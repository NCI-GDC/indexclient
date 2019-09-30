from indexclient.client import Document, IndexClient


class MockIndexClient(IndexClient):

    def __init__(self, baseurl, version="v0", auth=None):
        super(MockIndexClient, self).__init__(baseurl, version, auth)

    def get(self, did):
        return Document()

    def add_version(self, current_did, new_doc):
        pass

    def url_for(self, *path):
        return super(MockIndexClient, self).url_for(*path)

    def check_status(self):
        super(MockIndexClient, self).check_status()

    def global_get(self, did, no_dist=False):
        return super(MockIndexClient, self).global_get(did, no_dist)

    def bulk_request(self, dids):
        return super(MockIndexClient, self).bulk_request(dids)

    def bulk_get_latest(self, dids, skip_null=False):
        return super(MockIndexClient, self).bulk_get_latest(dids, skip_null)

    def get_with_params(self, params=None):
        return super(MockIndexClient, self).get_with_params(params)

    def list(self, limit=float("inf"), start=None, page_size=100):
        return super(MockIndexClient, self).list(limit, start, page_size)

    def list_with_params(self, limit=float("inf"), start=None, page_size=100, params=None, negate_params=None):
        return super(MockIndexClient, self).list_with_params(limit, start, page_size, params, negate_params)

    def create(self, hashes, size, did=None, urls=None, file_name=None, metadata=None, baseid=None, acl=None,
               urls_metadata=None, version=None):
        return super(MockIndexClient, self).create(hashes, size, did, urls, file_name, metadata, baseid, acl,
                                                   urls_metadata, version)

    def create_alias(self, record, size, hashes, release=None, metastring=None, host_authorities=None,
                     keeper_authority=None):
        return super(MockIndexClient, self).create_alias(record, size, hashes, release, metastring, host_authorities,
                                                         keeper_authority)

    def get_latest_version(self, did, skip_null_versions=False):
        return super(MockIndexClient, self).get_latest_version(did, skip_null_versions)

    def list_versions(self, did):
        return super(MockIndexClient, self).list_versions(did)

    def _get(self, *path, **kwargs):
        return super(MockIndexClient, self)._get(*path, **kwargs)

    def _post(self, *path, **kwargs):
        return super(MockIndexClient, self)._post(*path, **kwargs)

    def _put(self, *path, **kwargs):
        return super(MockIndexClient, self)._put(*path, **kwargs)

    def _delete(self, *path, **kwargs):
        return super(MockIndexClient, self)._delete(*path, **kwargs)


