import os
from typing import Iterator, Optional

import importlib_resources as resources
import pytest
from testcontainers import compose

from indexclient import client


@pytest.fixture(scope="session")
def services() -> Iterator[Optional[compose.DockerCompose]]:
    """Start external services via compose."""
    if os.getenv("CI"):
        # disable test containers in gitlab ci
        yield None
        return

    docker_resources = resources.files("tests.integration") / "docker"

    with (
        resources.as_file(docker_resources) as docker_dir,
        compose.DockerCompose(
            str(docker_dir),
            "docker-compose.yaml",
            pull=True,
        ) as containers,
    ):
        indexd_port = containers.get_service_port("indexd", 80)
        indexd_host = f"http://localhost:{indexd_port}"
        os.environ["INDEXD_HOST"] = indexd_host
        os.environ["INDEXD_USER"] = "admin"
        os.environ["INDEXD_PASS"] = "admin"
        containers.wait_for(url=f"{indexd_host}/_status")

        yield containers


@pytest.fixture(scope="function")
def index_client(services) -> client.IndexClient:
    """
    Handles getting all the docs from an
    indexing endpoint. Currently this is changing from
    signpost to indexd, so we'll use just indexd_client now.
    I.E. test to a common interface this could be multiply our
    tests:
    https://docs.pytest.org/en/latest/fixture.html#parametrizing-fixtures
    """
    return client.IndexClient(
        os.environ["INDEXD_HOST"],
        auth=(os.environ["INDEXD_USER"], os.environ["INDEXD_PASS"]),
    )
