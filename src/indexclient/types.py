import enum

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

from typing import Dict, List


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
    acl: List[str]
    did: str
    file_name: str
    form: str
    hashes: IndexHash
    metadata: IndexMetaData
    size: int
    urls: List[str]
    urls_metadata: Dict[str, UrlMetadata]
    version: str


class Form(enum.Enum):
    object = "object"
    container = "container"
    multipart = "multipart"
