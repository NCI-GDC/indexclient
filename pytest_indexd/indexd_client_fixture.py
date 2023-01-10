from typing import Iterable, List, Tuple, Union

import pytest
import yaml
from _pytest.fixtures import fixture

from indexclient.client import Document, IndexClient
from indexclient.types import IndexData
from pytest_indexd import hints
from pytest_indexd.indexd_server_fixture import MockServer
from pytest_indexd.utils import mock_doc


@pytest.fixture
def indexd_client(
    indexd_server: MockServer,
    create_indexd_tables: fixture,  # usefixtures will cause failure for this one
    indexd_admin_user: Tuple[str, str],
) -> IndexClient:
    """Create the tables and add an auth user"""
    return IndexClient(
        indexd_server.baseurl, auth=(indexd_admin_user[0], indexd_admin_user[1])
    )


@pytest.fixture()
def indexd_loader(indexd_client: IndexClient) -> hints.IndexRecordLoader:
    """Loads index documents from file"""

    def load(resource: Union[str, Iterable[IndexData]]) -> List[Document]:
        """Loads a resource

        Args:
            resource: either a filename (str) or an iterable of already loaded docs
        """
        docs: List[Document] = []
        docs_data: Iterable[IndexData] = resource

        if isinstance(resource, str):
            #  attempt to read from file
            with open(resource, "r") as f:
                doc_data = yaml.safe_load(f)
                docs_data = doc_data["docs"]

        for doc in docs_data:
            document = indexd_client.create(**mock_doc(doc))
            docs.append(document)
        return docs

    return load
