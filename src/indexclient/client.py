import copy
import json
import logging
from typing import Any, NamedTuple, TYPE_CHECKING
from urllib.parse import urljoin

import requests

from indexclient import errors
from indexclient.types import Form, IndexData, IndexHash, IndexMetaData

UPDATABLE_ATTRS = [
    "file_name",
    "urls",
    "version",
    "metadata",
    "acl",
    "urls_metadata",
    "hashes",
    "size",
]


class UrlMetadata(NamedTuple):
    url: str
    type: str
    state: str


def json_dumps(data: Any) -> str:
    return json.dumps({k: v for (k, v) in data.items() if v is not None})


def handle_error(resp: requests.Response) -> None:
    if 400 <= resp.status_code < 600:
        try:
            json = resp.json()
            resp.reason = json["error"]
        except KeyError:
            pass
        finally:
            resp.raise_for_status()


class IndexClient:
    def __init__(self, baseurl: str, version: str = "v0", auth: tuple[str, str] | None = None):
        self.auth = auth
        self.url = baseurl
        self.version = version

    def url_for(self, *path):
        return urljoin(self.url, "/".join(path))

    def check_status(self) -> None:
        """Check that the API we are trying to communicate with is online"""
        resp = requests.get(self.url + "/index")
        handle_error(resp)

    def global_get(self, did, no_dist=False) -> ["Document"]:
        """
        Makes a web request to the Indexd service global endpoint to retrieve
        an index document record.

        :param str did:
            The UUID for the index record we want to retrieve.

        :param boolean no_dist:
            *optional* Specify if we want distributed search or not

        :returns: A Document object representing the index record
        """
        try:
            if no_dist:
                response = self._get(did, params={"no_dist": ""})
            else:
                response = self._get(did)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            else:
                raise e

        return Document(self, did, json=response.json())

    def get(self, did):
        """
        Makes a web request to the Indexd service to retrieve an index document record.

        :param str did:
            The UUID for the index record we want to retrieve.

        :returns: A Document object representing the index record
        """
        try:
            response = self._get("index", did)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            else:
                raise e

        return Document(self, did, json=response.json())

    def bulk_request(self, dids):
        """
        bulk_get makes one http request to the indexd service and retrieves
        a list of Documents based on the dids provided.

        Args:
            dids (list): list of dids for potential documents
        Returns:
            list: Document objects representing  index records
        """

        headers = {"content-type": "application/json"}
        try:
            response = self._post("bulk/documents", json=dids, headers=headers)
        except requests.HTTPError as exception:
            if exception.response.status_code == 404:
                return None
            else:
                raise exception

        return [Document(self, doc["did"], json=doc) for doc in response.json()]

    def bulk_get_latest(self, dids, skip_null=False, exclude_deleted=False):
        """
        bulk get latest version
        Args:
            dids (list): list of dids
            skip_null (bool): skip null versions
            exclude_deleted (bool): exclude deleted versions

        Returns:
            list: Document objects

        """
        headers = {"content-type": "application/json"}
        try:
            response = self._post(
                "bulk/documents/latest",
                params={"skip_null": skip_null, "exclude_deleted": exclude_deleted},
                json=dids,
                headers=headers,
            )
        except requests.HTTPError as exception:
            if exception.response.status_code == 404:
                return None
            else:
                raise exception
        return [Document(self, doc["did"], json=doc) for doc in response.json()]

    def get_with_params(self, params=None):
        """
        Return a document object corresponding to the supplied parameters, such
        as ``{'hashes': {'md5': '...'}, 'size': '...', 'metadata': {'file_state': '...'}}``.
        """
        # need to include all the hashes in the request
        # index client like signpost or indexd will need to handle the
        # query param `'hash': 'hash_type:hash'`
        params_copy = copy.deepcopy(params) or {}
        if "hashes" in params_copy:
            params_copy["hash"] = params_copy.pop("hashes")
        reformatted_params = dict()
        for param in ["hash", "metadata"]:
            if param in params_copy:
                reformatted_params[param] = []
                for k, v in params_copy[param].items():
                    reformatted_params[param].append(str(k) + ":" + str(v))
                del params_copy[param]
        reformatted_params.update(params_copy)
        reformatted_params["limit"] = 1

        try:
            response = self._get("index", params=reformatted_params)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            else:
                raise e
        if not response.json()["records"]:
            return None
        json = response.json()["records"][0]
        did = json["did"]
        return Document(self, did, json=json)

    def list(self, limit=float("inf"), start=None, page_size=100):
        """Returns a generator of document objects."""
        return self.list_with_params(limit, start, page_size)

    def list_with_params(
        self,
        limit=float("inf"),
        start=None,
        page_size=100,
        params=None,
        negate_params=None,
    ):
        """
        Return a generator of document object corresponding to the supplied parameters, such
        as ``{'hashes': {'md5': '...'},
              'size': '...',
              'metadata': {'file_state': '...'},
              'urls_metadata': {'s3://url': {'state': '...'}
             }``.
        """
        params_copy = copy.deepcopy(params) or {}
        if "hashes" in params_copy:
            params_copy["hash"] = params_copy.pop("hashes")
        if "urls_metadata" in params_copy:
            params_copy["urls_metadata"] = json.dumps(params_copy.pop("urls_metadata"))
        reformatted_params = dict()
        for param in ["hash", "metadata"]:
            if param in params_copy:
                reformatted_params[param] = []
                for k, v in params_copy[param].items():
                    reformatted_params[param].append(str(k) + ":" + str(v))
                del params_copy[param]
        reformatted_params.update(params_copy)
        reformatted_params.update({"limit": page_size, "start": start})
        if negate_params:
            reformatted_params.update({"negate_params": json.dumps(negate_params)})
        yielded = 0
        while True:
            resp = self._get("index", params=reformatted_params)
            handle_error(resp)
            json_str = resp.json()
            if not json_str["records"]:
                return
            for doc in json_str["records"]:
                if yielded < limit:
                    yield Document(self, None, json=doc)
                    yielded += 1
                else:
                    return
            if len(json_str["records"]) == page_size:
                reformatted_params["start"] = json_str["records"][-1]["did"]
            else:
                # There's no more results
                return

    def create(
        self,
        hashes: Dict[str, str],
        size: int,
        did: Optional[str] = None,
        urls: Optional[List[str]] = None,
        file_name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        baseid: Optional[str] = None,
        acl: Optional[List[str]] = None,
        urls_metadata: Optional[Dict[str, Dict[str, str]]] = None,
        version: Optional[str] = None,
    ):
        """Create a new entry in indexd

        Args:
            hashes (dict): {hash type: hash value,}
                eg ``hashes={'md5': ab167e49d25b488939b1ede42752458b'}``
            size (int): file size metadata associated with a given uuid
            did (str): provide a UUID for the new indexd to be made
            urls (list): list of URLs where you can download the UUID
            acl (list): access control list
            file_name (str): name of the file associated with a given UUID
            metadata (dict): additional key value metadata for this entry
            urls_metadata (dict): metadata attached to each url
            baseid (str): optional baseid to group with previous entries versions
            version (str): entry version string
        Returns:
            Document: indexclient representation of an entry in indexd
        """

        if urls is None:
            urls = []
        json = {
            "urls": urls,
            "form": "object",
            "hashes": hashes,
            "size": size,
            "file_name": file_name,
            "metadata": metadata,
            "urls_metadata": urls_metadata,
            "baseid": baseid,
            "acl": acl,
            "version": version,
        }
        if did:
            json["did"] = did
        resp = self._post(
            "index/",
            headers={"content-type": "application/json"},
            data=json_dumps(json),
            auth=self.auth,
        )
        if resp.status_code == 200:
            return Document(self, resp.json()["did"])

        logging.error(resp.json())
        raise errors.BaseIndexError(resp.status_code, resp.text)

    def create_alias(
        self,
        record,
        size,
        hashes,
        release=None,
        metastring=None,
        host_authorities=None,
        keeper_authority=None,
    ):
        data = json_dumps(
            {
                "size": size,
                "hashes": hashes,
                "release": release,
                "metastring": metastring,
                "host_authorities": host_authorities,
                "keeper_authority": keeper_authority,
            }
        )
        url = "/alias/" + record
        headers = {"content-type": "application/json"}
        resp = self._put(url, headers=headers, data=data, auth=self.auth)
        return resp.json()

    def get_latest_version(self, did, skip_null_versions=False, exclude_deleted=False):
        """
        Get the latest version given did
        Args:
            did (str): document id of an existing entry whose latest version is requested
            skip_null_versions (bool): if True, exclude entries without a version
            exclude_deleted (bool): if True, exclude entries marked as deleted in metadata
        Returns:
            Document: latest version of the entry
        """

        params = {
            "has_version": json.dumps(skip_null_versions),
            "exclude_deleted": json.dumps(exclude_deleted),
        }
        doc = self._get("index", did, "latest", params=params).json()

        if doc and "did" in doc:
            return Document(self, doc["did"], doc)
        return None

    def add_version(self, current_did, new_doc):
        """

        Args:
            current_did (str): did of an existing index whose baseid will be shared
            new_doc (Document): the document version to add
        Return:
            Document: the version that was just added
        """

        rev_doc = self._post("index", current_did, json=new_doc.to_json(), auth=self.auth).json()
        if rev_doc and "did" in rev_doc:
            return Document(self, rev_doc["did"])
        return None

    def list_versions(self, did, exclude_deleted=False):
        """
        Get all record versions given did
        Args:
            did (str): document id of an existing record
            exclude_deleted (bool): if True, exclude records marked as deleted in metadata
        Returns:
            list: Document versions
        """

        params = {"exclude_deleted": json.dumps(exclude_deleted)}

        versions_dict = self._get("index", did, "versions", params=params).json()  # type: dict
        versions = []

        for version in versions_dict.values():
            versions.append(Document(self, version["did"], version))
        return versions

    def query_urls_metadata(
        self,
        url,
        key,
        value,
        fields=None,
        versioned=False,
        exclude_deleted=False,
        limit=100,
        offset=0,
        page_size=100,
    ):
        """Queries indexd entries using URL patterns, which can be either full or partial URLs
        Args:
            url (str): A URL pattern to match
            key (str): metadata key
            value (str): metadata value for key
            versioned (bool): whether or not is versioned
            exclude_deleted (bool): If true, exclude deleted documents from search
            fields: (str): comma separated list of fields to return
            limit: (int): max results to return
            offset: (int) where to start the next query from
            page_size (int): how many to query at a time
        Returns:
            Generator[Dict]: indexd entries
        """
        params = {
            "url": url,
            "key": key,
            "value": value,
            "fields": fields,
            "versioned": versioned,
            "exclude_deleted": exclude_deleted,
            "limit": limit if limit < page_size else page_size,
            "offset": offset,
        }

        while limit > 0:
            response = self._get("_query/urls/metadata/q", params=params).json()
            if not response:
                break
            yield from response

            limit -= len(response)
            params["limit"] = min(limit, page_size)
            params["offset"] += len(response)

    def query_url(
        self,
        exclude=None,
        include=None,
        versioned=False,
        exclude_deleted=False,
        fields=None,
        limit=100,
        offset=0,
        page_size=100,
    ):
        """Queries indexd entries using URL patterns, which can be either full or partial URLs
        Args:
            exclude (str): A URL pattern to exclude. All URLs matching this pattern will not be included in the return
            include (str): All entries with URL matching this pattern will be included
            versioned (bool): whether or not is versioned
            exclude_deleted (bool): if True, excludes deleted docs from search
            fields: (str): comma separated list of fields to return
            limit: (int): max results to return
            offset: (int) where to start the next query from
            page_size (int): how many to query at a time
        Returns:
            Generator[Dict]: indexd entries
        """
        params = {
            "exclude": exclude,
            "include": include,
            "versioned": versioned,
            "exclude_deleted": exclude_deleted,
            "fields": fields,
            "limit": limit if limit < page_size else page_size,
            "offset": offset,
        }
        while limit > 0:
            response = self._get("_query/urls/q", params=params).json()

            if not response:
                break
            yield from response

            limit -= len(response)
            params["limit"] = min(limit, page_size)
            params["offset"] += len(response)

    def _get(self, *path, **kwargs):
        resp = requests.get(self.url_for(*path), **kwargs)
        handle_error(resp)
        return resp

    def _post(self, *path, **kwargs):
        resp = requests.post(self.url_for(*path), **kwargs)
        handle_error(resp)
        return resp

    def _put(self, *path, **kwargs):
        resp = requests.put(self.url_for(*path), **kwargs)
        handle_error(resp)
        return resp

    def _delete(self, *path, **kwargs):
        resp = requests.delete(self.url_for(*path), **kwargs)
        handle_error(resp)
        return resp




def recursive_sort(value):
    """
    Sort all the lists in the dictionary recursively so that we can compare a
    dictionary's contents being the same instead of comparing their order.
    """
    if isinstance(value, dict):
        return {key: recursive_sort(value[key]) for key in value.keys()}
    elif isinstance(value, list):
        return sorted(recursive_sort(element) for element in value)
    else:
        return value
