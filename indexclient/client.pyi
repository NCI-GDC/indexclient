from typing import Dict, Iterable, List, Protocol

from indexclient.types import Form, IndexHash, IndexMetaData, UrlMetadata

class Document(Protocol):
    acl: List[str]
    baseid: str
    did: str
    file_name: str
    form: Form
    hashes: IndexHash
    metadata: IndexMetaData
    rev: str
    size: int
    urls: List[str]
    urls_metadata: Dict[str, UrlMetadata]
    version: str

    def patch(self): ...

class IndexClient(Protocol):
    def get(self, did: str) -> Document: ...
    def create(self, **kwargs) -> Document: ...
    def add_version(self, current_did: str, new_doc: Document) -> Document: ...
    def list_versions(self, did: str) -> Iterable[Document]: ...
    def bulk_request(self, dids: Iterable[str]) -> List[Document]: ...
