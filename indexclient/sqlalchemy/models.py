import datetime

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext import declarative

Base = declarative.declarative_base()


class IndexRecord(Base):
    """
    Base index record representation.
    """

    __tablename__ = "index_record"

    did = sa.Column(sa.String, primary_key=True)

    baseid = sa.Column(sa.String, index=True)
    rev = sa.Column(sa.String)
    form = sa.Column(sa.String)
    size = sa.Column(sa.BigInteger, index=True)
    release_number = sa.Column(sa.String, index=True)
    created_date = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    updated_date = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    file_name = sa.Column(sa.String, index=True)
    version = sa.Column(sa.String, index=True)
    uploader = sa.Column(sa.String, index=True)
    index_metadata = sa.Column(postgresql.JSONB)

    urls_metadata = orm.relationship(
        "IndexRecordUrlMetadata",
        backref="index_record",
        cascade="all, delete-orphan",
    )

    acl = orm.relationship(
        "IndexRecordACE",
        backref="index_record",
        cascade="all, delete-orphan",
    )

    hashes = orm.relationship(
        "IndexRecordHash",
        backref="index_record",
        cascade="all, delete-orphan",
    )

    aliases = orm.relationship(
        "IndexRecordAlias",
        backref="index_record",
        cascade="all, delete-orphan",
    )

    def as_dict(self):
        """
        Get the full index document
        """
        urls = [u.url for u in self.urls_metadata]
        acl = [u.ace for u in self.acl]
        hashes = {h.hash_type: h.hash_value for h in self.hashes}
        metadata = self.index_metadata or {}

        # Add this field back to the returned metadata json section. This
        # allows current clients to function without change.
        # If it doesn't exist then don't return the key in the json.
        if self.release_number:
            metadata["release_number"] = self.release_number

        # urls_metadata = extract_urls_metadata(self.urls_metadata)
        created_date = self.created_date.isoformat()
        updated_date = self.updated_date.isoformat()

        return dict(
            did=self.did,
            baseid=self.baseid,
            rev=self.rev,
            size=self.size,
            file_name=self.file_name,
            version=self.version,
            uploader=self.uploader,
            urls=urls,
            urls_metadata={},
            acl=acl,
            hashes=hashes,
            metadata=metadata,
            form=self.form,
            created_date=created_date,
            updated_date=updated_date,
        )


class IndexRecordAlias(Base):
    """
    Alias attached to index record
    """

    __tablename__ = "index_record_alias"

    did = sa.Column(sa.String, sa.ForeignKey("index_record.did"), primary_key=True)
    name = sa.Column(sa.String, primary_key=True)

    __table_args__ = (
        sa.Index("index_record_alias_idx", "did"),
        sa.Index("index_record_alias_name", "name"),
    )


class IndexRecordUrl(Base):
    """
    Base index record url representation.
    """

    __tablename__ = "index_record_url"

    did = sa.Column(sa.String, primary_key=True)
    url = sa.Column(sa.String, primary_key=True)
    __table_args__ = (sa.Index("index_record_url_idx", "did"),)


class IndexRecordACE(Base):
    """
    index record access control entry representation.
    """

    __tablename__ = "index_record_ace"

    did = sa.Column(sa.String, sa.ForeignKey("index_record.did"), primary_key=True)
    # access control entry
    ace = sa.Column(sa.String, primary_key=True)

    __table_args__ = (sa.Index("index_record_ace_idx", "did"),)


class IndexRecordUrlMetadata(Base):
    """
    Metadata attached to url in jsonb format
    """

    __tablename__ = "index_record_url_metadata_jsonb"
    did = sa.Column(sa.String, primary_key=True)
    url = sa.Column(sa.String, primary_key=True)
    type = sa.Column(sa.String, index=True)
    state = sa.Column(sa.String, index=True)
    urls_metadata = sa.Column(postgresql.JSONB)
    __table_args__ = (sa.ForeignKeyConstraint(("did",), ["index_record.did"]),)


class IndexRecordHash(Base):
    """
    Base index record hash representation.
    """

    __tablename__ = "index_record_hash"
    did = sa.Column(sa.String, sa.ForeignKey("index_record.did"), primary_key=True)
    hash_type = sa.Column(sa.String, primary_key=True)
    hash_value = sa.Column(sa.String)
    __table_args__ = (
        sa.Index("index_record_hash_idx", "did"),
        sa.Index("index_record_hash_type_value_idx", "hash_value", "hash_type"),
    )
1
