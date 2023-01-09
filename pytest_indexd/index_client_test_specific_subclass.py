import uuid
from typing import Dict, Iterable, List, Optional

import pytest
from indexdmodels.sqlalchemy import models, sessions

from indexclient.client import Document


class IndexClientTestSpecificSubclass:
    def __init__(self, pg_url, *args, **kwargs):
        self.driver = sessions.IndexdDatabaseDriver(pg_url, read_only=False)

    def url_for(self, *path):
        raise NotImplementedError

    def check_status(self):
        raise NotImplementedError

    def get(self, did):
        """
        Retrieve an index document record.

        :param str did:
            The UUID for the index record we want to retrieve.

        :returns: A Document object representing the index record
        """
        with self.driver.transaction() as t:
            record = t.query(models.IndexRecord).get(did)
        return Document(None, did, dict(record))

    def create(
        self,
        hashes: Optional[Dict[str, str]] = None,
        size: Optional[int] = None,
        did: Optional[str] = None,
        urls: Optional[Iterable[str]] = None,
        file_name: Optional[str] = None,
        metadata: Optional[Dict] = None,
        baseid: Optional[str] = None,
        acl: Optional[Iterable[str]] = None,
        urls_metadata: Optional[Dict] = None,
        version: Optional[str] = None,
        uploader: Optional[str] = None,
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
        urls = urls or []
        acl = acl or []
        hashes = hashes or {}
        metadata = metadata or {}
        urls_metadata = urls_metadata or {}
        did = did or str(uuid.uuid4())
        baseid = baseid or str(uuid.uuid4())

        assert sorted(urls) == sorted(
            urls_metadata.keys()
        ), "urls and urls_metadata mismatch"

        with self.driver.transaction() as t:
            record_acl = [models.IndexRecordACE(did=did, ace=ace) for ace in acl]
            record_hashes = [
                models.IndexRecordHash(did=did, hash_type=t, hash_value=v)
                for t, v in hashes.items()
            ]
            record_url_metadata = []

            for url, url_metadata in urls_metadata.items():
                u_type = url_metadata.get("type")
                u_state = url_metadata.get("state")

                record_url_metadata.append(
                    models.IndexRecordUrlMetadata(
                        did=did,
                        url=url,
                        type=u_type,
                        state=u_state,
                        urls_metadata=url_metadata,
                    )
                )

            record = models.IndexRecord(
                did=did,
                baseid=baseid,
                file_name=file_name,
                version=version,
                rev=str(uuid.uuid4())[:8],
                size=size,
                index_metadata=metadata,
                acl=record_acl,
                hashes=record_hashes,
                urls_metadata=record_url_metadata,
                uploader=uploader,
            )
            t.add(record)
            t.commit()

            return Document(None, did, dict(record))


@pytest.fixture
def indexd_client_tss(pg_url, create_indexd_tables):
    return IndexClientTestSpecificSubclass(pg_url)
