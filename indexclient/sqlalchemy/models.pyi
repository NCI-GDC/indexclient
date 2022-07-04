import datetime
from typing import List, Dict, Tuple, Type

from sqlalchemy import Index, orm
from sqlalchemy.ext.declarative import DeclarativeMeta

from indexclient import client

Base: Type[DeclarativeMeta]

class IndexTable(Base):
    __tablename__: str
    __table_args__: Tuple[Index, ...]
    did: str


class IndexRecordACE(IndexTable):
    ace: orm.Mapped[str]


class IndexRecordUrl(IndexTable):
    url: orm.Mapped[str]


class IndexRecordUrlMetadata(IndexTable):
    url: orm.Mapped[str]
    type: orm.Mapped[str]
    state: orm.Mapped[str]
    urls_metadata: orm.Mapped[Dict[str, str]]


class IndexRecordHash(IndexTable):
    hash_type: orm.Mapped[str]
    hash_value: orm.Mapped[str]


class IndexRecordAlias(IndexTable):
    name: orm.Mapped[str]

class IndexRecord(IndexTable):
    baseid: orm.Mapped[str]
    rev: orm.Mapped[str]
    form: orm.Mapped[str]
    size: orm.Mapped[int]
    release_number: orm.Mapped[str]
    created_date: datetime.datetime
    updated_date: datetime.datetime
    file_name: orm.Mapped[str]
    version: orm.Mapped[str]
    uploader: orm.Mapped[str]
    acl: List[IndexRecordACE]
    hashes: List[IndexRecordHash]
    aliases: List[IndexRecordAlias]
    urls_metadata: List[IndexRecordUrlMetadata]
    index_metadata: List[client.IndexMetaData]

    def as_dict(self) -> client.DocumentDict:
        ...
