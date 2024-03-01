import deepdiff
import importlib_resources
import yaml

from indexclient.client import IndexClient
from pytest_indexd import hints
from pytest_indexd.fixtures.indexd_models_fixture import IndexdDriverWrapper


def test_indexd_loader_dict(
    indexd_loader: hints.IndexRecordLoader, indexd_client: IndexClient
) -> None:
    docs_data = (
        importlib_resources.files("tests.data")
        .joinpath("dat_3021_indexd_sample.yaml")
        .read_text()
    )
    data = yaml.safe_load(docs_data)
    indexd_loader(resource=data["docs"])

    assert len(list(indexd_client.list())) == 5


def test_indexd_loader_yaml(
    indexd_loader: hints.IndexRecordLoader, indexd_client: IndexClient
) -> None:
    docs_data = importlib_resources.files("tests.data").joinpath("dat_3021_indexd_sample.yaml")
    indexd_loader(resource=docs_data)

    assert len(list(indexd_client.list())) == 5


def test_indexd_loader_json(
    indexd_loader: hints.IndexRecordLoader, indexd_client: IndexClient
) -> None:
    docs_data = importlib_resources.files("tests.data").joinpath("documents.json")

    indexd_loader(resource=docs_data)

    assert len(list(indexd_client.list())) == 5


def test_indexd_driver_wrapper_get(
    indexd_loader: hints.IndexRecordLoader,
    indexd_client: IndexClient,
    indexd_driver_wrapper: IndexdDriverWrapper,
) -> None:
    docs_data = importlib_resources.files("tests.data").joinpath("documents.json")

    indexd_loader(resource=docs_data)

    expected = indexd_client.get("317f2c0d-bb9f-4924-bedc-d09275a85da4").to_json()

    doc_dict = indexd_driver_wrapper.get("317f2c0d-bb9f-4924-bedc-d09275a85da4").to_json()

    assert deepdiff.DeepDiff(doc_dict, expected, ignore_order=True) == {}
