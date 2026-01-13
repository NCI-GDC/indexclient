import copy
import json
import logging
from typing import Any, NamedTuple, TYPE_CHECKING
from urllib.parse import urljoin

import requests

from indexclient import errors
from dataclasses import dataclass
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


class DocumentDeletedError(Exception):
    pass


DocValueType = list[str] | str | None
@dataclass
class Document:
    did: str
    json: dict | None = None
    
    def __init__(self, did: str, json: dict | None = None) -> None:
        self._doc: dict[str, DocValueType] = {}
        self.did = did
        self._fetched = False
        self._deleted = False
        self._load(json)

    @property
    def acl(self) -> DocValueType:
        return self._doc.setdefault("acl", [])

    @acl.setter
    def acl(self, new_acl: list[str]) -> None:
        self._doc["acl"] = new_acl

    @property
    def baseid(self) -> DocValueType:
        return self._doc.get("baseid")

    @baseid.setter
    def baseid(self, new_baseid: str) -> None:
        self._doc["baseid"] = new_baseid

    @property
    def did(self) -> DocValueType:
        return self._doc.get("did")

    @did.setter
    def did(self, new_did: str) -> None:
        self._doc["did"] = new_did

    @property
    def file_name(self) -> str | None:
        return self._doc.get("file_name")

    @file_name.setter
    def file_name(self, new_file_name: str) -> None:
        self._doc["file_name"] = new_file_name

    @property
    def form(self) -> Form | None:
        return self._doc.get("form")

    @form.setter
    def form(self, new_form: Form) -> None:
        self._doc["form"] = new_form

    @property
    def hashes(self) -> IndexHash:
        return self._doc.setdefault("hashes", {})

    @hashes.setter
    def hashes(self, new_hashes: IndexHash) -> None:
        self._doc["hashes"] = new_hashes

    @property
    def metadata(self) -> IndexMetaData | None:
        return self._doc.get("metadata")

    @metadata.setter
    def metadata(self, new_metadata: IndexMetaData) -> None:
        self._doc["metadata"] = new_metadata

    @property
    def rev(self) -> str | None:
        return self._doc.get("rev")

    @rev.setter
    def rev(self, new_rev) -> None:
        self._doc["rev"] = new_rev

    @property
    def size(self) -> int | None:
        return self._doc.get("size")

    @size.setter
    def size(self, new_size: int) -> None:
        self._doc["size"] = new_size

    @property
    def urls(self) -> list[str]:
        return self._doc.setdefault("urls", [])

    @urls.setter
    def urls(self, new_urls: list[str]) -> None:
        self._doc["urls"] = new_urls

    @property
    def urls_metadata(self) -> dict[str, UrlMetadata]:
        return self._doc.setdefault("urls_metadata", {})

    @urls_metadata.setter
    def urls_metadata(self, new_urls_metadata: dict[str, UrlMetadata]):
        self._doc["urls_metadata"] = new_urls_metadata

    @property
    def version(self) -> str | None:
        return self._doc.get("version")

    @version.setter
    def version(self, new_version: str) -> None:
        self._doc["version"] = new_version

    @property
    def uploader(self) -> str | None:
        return self._doc.get("uploader")

    @uploader.setter
    def uploader(self, new_uploader: str) -> None:
        self._doc["uploader"] = new_uploader

    @property
    def created_date(self) -> str | None:
        return self._doc.get("created_date")

    @created_date.setter
    def created_date(self, new_date: str) -> None:
        self._doc["created_date"] = new_date

    @property
    def updated_date(self) -> str | None:
        return self._doc.get("updated_date")

    @updated_date.setter
    def updated_date(self, new_date: str) -> None:
        self._doc["updated_date"] = new_date

    def __eq__(self, other_doc):
        """
        equals `==` operator overload
        """
        return self.did == other_doc.did

    def __ne__(self, other_doc):
        """
        not equals `!=` operator overload
        """
        return self.did != other_doc.did

    def __hash__(self):
        return hash(self.did)

    def __lt__(self, other_doc):
        return self.did < other_doc.did

    def __gt__(self, other_doc):
        return self.did > other_doc.did

    def __repr__(self):
        """
        String representation of a Document

        Example:
            <Document(size=1, form=object, file_name=filename.txt, ...)>
        """
        attributes = ", ".join([f"{attr}={self._doc[attr]}" for attr in self._attrs])
        return "<Document(" + attributes + ")>"

    def _check_deleted(self):
        if self._deleted:
            raise DocumentDeletedError(f"document {self.did} has been deleted")

    def _render(self) -> dict:
        self._check_deleted()
        if not self._fetched:
            raise RuntimeError(
                "Document must be fetched from the server before being rendered as json"
            )
        return self._doc

    def to_json(self, include_rev: bool = True) -> Dict[str, Any]:
        json = self._render(include_rev=include_rev)
        if not self.did:
            del json["did"]
        return json

    # TODO: Fix this to remove circular dependency.
    # Client object should accept Document object for lookups?
    def _load(self, json: Optional[IndexData] = None):
        """Load the document contents from the server or from the provided dictionary"""
        self._check_deleted()
        json = json or self.client._get("index", self.did).json()
        # set attributes to current Document
        for k, v in json.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                logging.warning(f"Extra data {k}={v} not handled by indexclient")
        self._attrs = json.keys()
        self._fetched = True

    def _doc_for_update(self):
        """
        return document with subset of attributes that are allowed
        to be updated
        """
        return {k: v for k, v in self._doc.items() if k in UPDATABLE_ATTRS}

    @property
    def _sorted_doc(self):
        """Return the _doc object but with all arrays in sorted order.

        This will allow us to compare dictionaries with lists correctly. We
        only care about the contents of the arrays not the order of them.
        """
        return recursive_sort(self._doc)

    def patch(self):
        """Update attributes in an indexd Document

        "Patch" the current document attributes then upload the
        changed result to the indexd server.
        """

        self._check_deleted()
        self.client._put(
            "index",
            self.did,
            params={"rev": self.rev},
            headers={"content-type": "application/json"},
            auth=self.client.auth,
            data=json.dumps(self._doc_for_update()),
        )
        self._load()  # to sync new rev from server

    # TODO: Fix this to remove circular dependency.
    def delete(self):
        self._check_deleted()
        self.client._delete("index", self.did, auth=self.client.auth, params={"rev": self.rev})
        self._deleted = True

    # TODO: Fix this to remove circular dependency.
    def get_url_metadata_by_type(self, url_type):
        """
        Gets the corresponding url_metadata with specified url_type.

        Parameters:
            url_type (str): desired type of URL

        Returns:
            A UrlMetadata object representing the metadata
        """
        urls_metadata = self._doc.get("urls_metadata", {})
        requested_metadata = [
            UrlMetadata(
                url=url,
                state=metadata.get("state"),
                type=metadata.get("type"),
            )
            for url, metadata in urls_metadata.items()
            if metadata.get("type") == url_type
        ]

        # Edge case, the following check can be removed after DEV-983
        if len(requested_metadata) > 1:
            raise ValueError("multiple urls of the request type within this Document")

        if requested_metadata:
            return requested_metadata[0]
        else:
            return None

    def get_url_by_url_type(self, url_type):
        """
        Gets the URL of the requested url_type from the document

        Parameters:
            url_type (str): the requested type of URL

        Returns:
            str: the URL of requested url type
        """
        url_metadata = self.get_url_metadata_by_type(url_type=url_type)
        if url_metadata:
            return url_metadata.url
        else:
            return None

    def get_state_by_url_type(self, url_type):
        """
        Gets state of the requested url_type from the document

        Parameters:
            url_type (str): the requested type of URL

        Returns:
            str: the state of requested url_type
        """
        url_metadata = self.get_url_metadata_by_type(url_type=url_type)
        if url_metadata:
            return url_metadata.state
        else:
            return None


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
