from typing import Dict, Iterable, List, Protocol, TypedDict

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

class IndexDocument(Protocol):
    acl: List[str]
    did: str
    size: int
    urls: List[str]
    hashes: IndexHash
    version: str
    metadata: IndexMetaData
    urls_metadata: Dict[str, UrlMetadata]

    def patch(self): ...

class IndexClient(Protocol):
    def get(self, did: str) -> IndexDocument: ...
    def create(self, **kwargs) -> IndexDocument: ...
    def add_version(
        self, current_did: str, new_doc: IndexDocument
    ) -> IndexDocument: ...
    def list_versions(self, did: str) -> Iterable[IndexDocument]: ...
    def bulk_request(self, dids: Iterable[str]) -> List[IndexDocument]: ...
