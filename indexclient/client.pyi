from typing import Dict, Iterable, List, Protocol

class Document(Protocol):
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
    def get(self, did: str) -> Document: ...
    def create(self, **kwargs) -> Document: ...
    def add_version(self, current_did: str, new_doc: Document) -> Document: ...
    def list_versions(self, did: str) -> Iterable[Document]: ...
    def bulk_request(self, dids: Iterable[str]) -> List[Document]: ...
