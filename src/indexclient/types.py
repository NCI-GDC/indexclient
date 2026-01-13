import enum

from typing import TypedDict

class UrlMetadata(TypedDict):
    state: str
    type: str


class IndexMetaData(TypedDict, total=False):
    gencode_version: str
    release: str
    version: str


class IndexHash(TypedDict, total=False):
    md5: str
    sha256: str


class IndexData(TypedDict, total=False):
    acl: list[str]
    did: str
    file_name: str
    form: str
    hashes: IndexHash
    metadata: IndexMetaData
    size: int
    urls: list[str]
    urls_metadata: dict[str, UrlMetadata]
    version: str


class Form(enum.Enum):
    object = "object"
    container = "container"
    multipart = "multipart"
