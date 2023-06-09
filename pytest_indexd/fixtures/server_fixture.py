"""Module for indexd_server fixture

The indexd_server fixture start up a test indexd server, runs on random ports between
8000 and 9000. We use random ports so we can parallel testing. This server save data to
postgres db. index_client fixture is usually used to interact with this server for
testing.
"""
import os
import random
import socket
import threading
from typing import Union

import flask
import pytest
import requests
from indexd import app_init

from pytest_indexd.fixtures import indexd_settings


class MockServer:
    def __init__(self, host: str, port: Union[int, str]):
        self.host = host
        self.port = port
        self.baseurl = f"http://{host}:{port}"


@pytest.fixture(scope="session")
def indexd_server(pg_url: str) -> MockServer:
    """
    Starts the indexd server, and cleans up its mess.
    Most tests will use the client which stems from this
    server fixture.

    Runs once per test session.
    """
    app = flask.Flask("indexd")
    # the side effect of the following line creates the db and tables.
    settings = indexd_settings.get_settings(pg_url)
    app_init(app, settings)

    host = "localhost"

    debug = os.getenv("DEBUG", False)
    port = get_available_port(host)

    t = threading.Thread(
        target=app.run, kwargs={"host": host, "port": port, "debug": debug}
    )
    t.setDaemon(True)
    t.start()

    wait_for_indexd_alive(host, port)
    yield MockServer(host=host, port=port)


def get_available_port(host):
    port = random.randint(8000, 9000)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        while sock.connect_ex((host, port)) == 0:
            port = random.randint(8000, 9000)
    return port


def wait_for_indexd_alive(host, port):
    url = f"http://{host}:{port}"
    try:
        requests.get(url)
    except requests.ConnectionError:
        return wait_for_indexd_alive(host, port)
    else:
        return
