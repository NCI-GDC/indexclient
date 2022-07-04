from typing_extensions import Protocol, TypedDict

from typing import (
    Dict,
    Iterable,
    List,
    Tuple,
    Optional,
    Union,
    Any,
    NamedTuple,
    Literal,
)

from requests import Response

IndexFileLocationType = Literal[
    "aws_archive",
    "aws_s3",
    "aws_s3_gl",
    "aws_s3_rr",
    "blackpearl-primary",
    "cleversafe",
    "primary-backup",
]

IndexFileState = Literal[
    "backing_up",
    "backuped",
    "deleted",
    "error",
    "failed",
    "registered",
    "uploaded",
    "uploading",
    "validated",
    "validating",
]

class URLMetadataTuple(NamedTuple):
    url: str
    type: IndexFileLocationType
    state: IndexFileState

class UrlMetadataDict(TypedDict):
    state: IndexFileState
    type: IndexFileLocationType

class IndexMetaData(TypedDict, total=False):
    gencode_version: Literal["neutral", "v22", "v36"]
    release: str
    version: str

class IndexHashes(TypedDict, total=False):
    md5: str
    sha256: str

class DocumentDict(TypedDict, total=False):
    did: str
    form: str
    size: int
    acl: List[str]
    rev: str
    urls: List[str]
    hashes: IndexHashes
    version: str
    metadata: IndexMetaData
    urls_metadata: Dict[str, UrlMetadataDict]

class Document(Protocol):

    _doc: DocumentDict
    _deleted: bool = False
    _fetched: bool = False

    client: "IndexClient"
    acl: List[str]
    did: str
    rev: str
    size: int
    urls: List[str]
    hashes: IndexHashes
    version: str
    metadata: IndexMetaData
    urls_metadata: Dict[str, UrlMetadataDict]
    def __init__(
        self,
        client: "IndexClient",
        did: Optional[str],  # allows passing in None value
        json: Optional[DocumentDict] = None,
    ) -> None: ...
    def to_json(self, include_rev: bool = True) -> DocumentDict: ...
    def patch(self) -> None: ...
    def delete(self) -> None: ...
    def get_url_metadata_by_type(self, url_type: str) -> URLMetadataTuple: ...
    def get_url_by_url_type(self, url_type: str) -> str: ...
    def get_state_by_url_type(self, url_type: str) -> str: ...
    def _doc_for_update(self) -> DocumentDict: ...
    def _load(self, json: Optional[DocumentDict] = None):
        """Attempts to load a document from the provided json or using the did"""
        ...
    def _check_deleted(self) -> None:
        """Check if a document has been deleted on the server"""
        ...
    def _render(self, include_rev: bool = True) -> DocumentDict: ...

class IndexSearchParameters(DocumentDict, total=False):
    ids: List[str]
    file_name: str
    start: int

class UrlQueryResult(TypedDict):
    did: str
    rev: str
    urls: List[str]

class IndexClient(Protocol):
    url: str
    version: str
    auth: Tuple[str, str]
    def __init__(
        self, baseurl: str, version: str = "v0", auth: Optional[Tuple[str, str]] = None
    ) -> None: ...
    def url_for(self, *path: str) -> str: ...
    def check_status(self) -> None: ...
    def global_get(self, did: str, no_dist: bool = False) -> Document: ...
    def get(self, did: str) -> Document: ...
    def bulk_request(self, dids: Iterable[str]) -> Iterable[Document]: ...
    def bulk_get_latest(
        self, dids: Iterable[str], skip_null: bool = False, skip_deleted: bool = True
    ) -> Iterable[Document]: ...
    def get_with_params(
        self, param: Optional[IndexSearchParameters] = None
    ) -> Document: ...
    def list_with_params(
        self,
        limit: float = float("inf"),
        start: Optional[int] = None,
        page_size: int = 100,
        params: Optional[IndexSearchParameters] = None,
        negate_params: Optional[IndexSearchParameters] = None,
    ) -> Iterable[Document]: ...
    def list(
        self,
        limit: float = float("inf"),
        start: Optional[int] = None,
        page_size: int = 100,
    ) -> Iterable[Document]: ...
    def create(
        self,
        hashes: IndexHashes,
        size: int,
        did: Optional[str] = None,
        urls: Optional[List[str]] = None,
        file_name: Optional[str] = None,
        metadata: Optional[IndexMetaData] = None,
        baseid: Optional[str] = None,
        acl: Optional[List[str]] = None,
        urls_metadata: Optional[Dict[str, UrlMetadataDict]] = None,
        version: Optional[str] = None,
    ) -> Document: ...
    def create_alias(
        self,
        record: str,
        size: int,
        hashes: IndexHashes,
        release: Optional[str] = None,
        metastring: Optional[str] = None,
        host_authorization: Optional[str] = None,
        keeper_authority: Optional[str] = None,
    ) -> Dict: ...
    def get_latest_version(
        self,
        did: str,
        skip_null_versions: bool = False,
        skip_deleted_version: bool = True,
    ) -> Document: ...
    def add_version(self, current_did: str, new_doc: Document) -> Document: ...
    def list_versions(self, did: str) -> Iterable[Document]: ...
    def query_urls_metadata(
        self,
        url: str,
        key: str,
        value: Union[bool, float, int, str],
        versioned: bool = False,
        fields: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        page_size: int = 100,
    ) -> UrlQueryResult: ...
    def query_url(
        self,
        exclude: Optional[str] = None,
        include: Optional[str] = None,
        versioned: bool = False,
        fields: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        page_size: int = 100,
    ) -> UrlQueryResult: ...
    # see https://peps.python.org/pep-0484/#arbitrary-argument-lists-and-default-argument-values
    def _get(self, *path: str, **kwargs: Any) -> Response: ...
    def _put(self, *path: str, **kwargs: Any) -> Response: ...
    def _post(self, *path: str, **kwargs: Any) -> Response: ...
    def _delete(self, *path: str, **kwargs: Any) -> Response: ...

def recursive_sort(value: Union[Dict, List, Any]) -> Union[Dict, List, Any]: ...
