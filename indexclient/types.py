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
    did: str
    form: str
    size: int
    acl: List[str]
    urls: List[str]
    hashes: IndexHash
    version: str
    metadata: IndexMetaData
    urls_metadata: Dict[str, UrlMetadata]
