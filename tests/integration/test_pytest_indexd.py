import importlib_resources
import yaml

from pytest_indexd import hints


def test_indexd_loader_dict(
    indexd_loader: hints.IndexRecordLoader, indexd_client
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
    indexd_loader: hints.IndexRecordLoader, indexd_client
) -> None:
    docs_data = importlib_resources.files("tests.data").joinpath(
        "dat_3021_indexd_sample.yaml"
    )
    indexd_loader(resource=docs_data)

    assert len(list(indexd_client.list())) == 5


def test_indexd_loader_json(
    indexd_loader: hints.IndexRecordLoader, indexd_client
) -> None:
    docs_data = importlib_resources.files("tests.data").joinpath("documents.json")

    indexd_loader(resource=docs_data)

    assert len(list(indexd_client.list())) == 5
