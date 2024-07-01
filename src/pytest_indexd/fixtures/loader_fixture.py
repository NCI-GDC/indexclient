"""THis module contains indexd_loader fixture.

The indexd_loader fixture will help to load test data on to test postgres db. This fixture
talks to postgres directly and should be faster than loading data through indexclient.
"""

import json
from pathlib import PosixPath
from typing import Iterable, List, Union

import pytest
import yaml

from indexclient.client import Document
from indexclient.types import IndexData
from pytest_indexd import hints
from pytest_indexd.fixtures.indexd_models_fixture import IndexdDriverWrapper
from pytest_indexd.utils import mock_doc


@pytest.fixture()
def indexd_loader(
    indexd_driver_wrapper: IndexdDriverWrapper,
) -> hints.IndexRecordLoader:
    """Loads index documents from file"""

    def load(resource: Union[str, Iterable[IndexData]]) -> List[Document]:
        """Loads a resource

        Args:
            resource: either a filename (str) or an iterable of already loaded docs
        """
        docs: List[Document] = []
        docs_data: Iterable[IndexData] = resource

        if isinstance(resource, str) or isinstance(resource, PosixPath):
            #  attempt to read from file
            with open(resource) as f:
                try:
                    doc_data = yaml.safe_load(f)
                except yaml.scanner.ScannerError:
                    doc_data = json.loads(f)
                docs_data = doc_data["docs"]

        for doc in docs_data:
            document = indexd_driver_wrapper.create(**mock_doc(doc))
            docs.append(document)
        return docs

    return load
