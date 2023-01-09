import uuid
from typing import Dict, Iterable, List, Optional

import pytest
import sqlalchemy
from indexdmodels.sqlalchemy import models, sessions
from requests import HTTPError
from sqlalchemy import and_, func
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

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
        return Document(None, did, record)

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

    def list_with_params(
        self,
        limit: int = float("inf"),
        start: Optional[str] = None,
        page_size: int = 100,
        params: Optional[Dict] = None,
        negate_params: Optional[Dict] = None,
    ):
        """Return a generator of document object corresponding to the supplied parameters.

        example: ``{'hashes': {'md5': '...'},
              'size': '...',
              'metadata': {'file_state': '...'},
              'urls_metadata': {'s3://url': {'state': '...'}
             }``.
        """
        with self.driver.transaction() as transaction:
            query = transaction.query(models.IndexRecord)

            query = query.options(joinedload(models.IndexRecord.urls_metadata))
            query = query.options(joinedload(models.IndexRecord.acl))
            query = query.options(joinedload(models.IndexRecord.hashes))
            query = query.options(joinedload(models.IndexRecord.aliases))

            if start is not None:
                query = query.filter(models.IndexRecord.did > start)

            params = params or {}
            for s in ("size", "file_name", "version", "uploader", "release_number"):
                value = params.get(s)
                if value is not None:
                    query = query.filter(getattr(models.IndexRecord, s) == s)

            for s in ("urls", "acl", "metadata", "urls_metadata"):
                value = params.get(s)
                if value:
                    raise NotImplementedError(f"param {s} not implemented")

            hashes = params.get("hashes")
            if hashes:
                for hash_type, hash_value in hashes.items():
                    sub = transaction.query(models.IndexRecordHash.did)
                    sub = sub.filter(
                        and_(
                            models.IndexRecordHash.hash_type == hash_type,
                            models.IndexRecordHash.hash_value == hash_value,
                        )
                    )
                    query = query.filter(models.IndexRecord.did.in_(sub.subquery()))

            if negate_params:
                query = self._negate_filter(query, **negate_params)

            return (Document(None, r.did, dict(r)) for r in query)

    def _negate_filter(
        self,
        query: sqlalchemy.orm.query,
        urls: Optional[List[str]] = None,
        acl: List[str] = None,
        file_name=None,
        version=None,
        metadata=None,
        urls_metadata=None,
    ):
        """
        param_values passed in here will be negated
        for string (version, file_name), filter with value != <value>
        for list (urls, acl), filter with doc that don't HAS <value>
        for dict (metadata, urls_metadata). In each (key,value) pair:
        - if value is None or empty: then filter with key doesn't exist
        - if value is provided, then filter with value != <value> OR key doesn't exist
        Args:
            session: db session
            query: sqlalchemy query
            urls (list): doc.urls don't have any <url> in the urls list
            acl (list): doc.acl don't have any <acl> in the acl list
            file_name (str): doc.file_name != <file_name>
            version (str): doc.version != <version>
            metadata (dict): see above for dict
            urls_metadata (dict): see above for dict
        Returns:
            Database query
        """
        if urls or acl or file_name or metadata or urls_metadata:
            raise NotImplementedError(
                f"param not implemented in _negate_filter {self.__class__.__name__}"
            )
        if version is not None:
            query = query.filter(models.IndexRecord.version != version)
        return query

    def get_latest_version(
        self, did, skip_null_versions=False, skip_deleted_versions=True
    ):
        """
        Get the latest version given did
        Args:
            did (str): document id of an existing entry whose latest version is requested
            skip_null_versions (bool): if True, exclude entries without a version
            skip_deleted_versions (bool): if True, exclude entries marked as deleted in metadata
        Returns:
            Document: latest version of the entry
        """

        try:
            uuid.UUID(did)
        except ValueError:
            raise HTTPError

        with self.driver.transaction() as transaction:
            query = transaction.query(models.IndexRecord)
            query = query.filter(models.IndexRecord.did == did)

            try:
                record = query.one()
                baseid = record.baseid
            except NoResultFound:
                baseid = did

            query = transaction.query(models.IndexRecord)
            query = query.filter(models.IndexRecord.baseid == baseid).order_by(
                models.IndexRecord.created_date.desc()
            )
            if skip_null_versions:
                query = query.filter(models.IndexRecord.version.isnot(None))
            if skip_deleted_versions:
                query = query.filter(
                    (
                        func.lower(models.IndexRecord.index_metadata["deleted"].astext)
                        == "true"
                    ).isnot(True)
                )
            record = query.first()
            return Document(None, record.did, dict(record))


@pytest.fixture
def indexd_client_tss(pg_url, create_indexd_tables):
    return IndexClientTestSpecificSubclass(pg_url)
