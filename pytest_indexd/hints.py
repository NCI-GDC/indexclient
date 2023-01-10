try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol

from typing import Iterable, Union

from indexclient.client import Document
from indexclient.types import IndexData


class IndexRecordLoader(Protocol):
    def __call__(self, resource: Union[str, Iterable[IndexData]]) -> Iterable[Document]:
        ...
