import importlib
import json
import os
import tempfile
from pathlib import Path

import pytest
import requests

from aana.configs.db import DbSettings, SQLiteConfig
from aana.storage.op import DbType
from aana.utils.json import jsonify


def call_streaming_endpoint(
    port: int, route_prefix: str, endpoint: str, data: dict
) -> list:
    """Call a streaming endpoint.

    Args:
        port (int): Port of the server.
        route_prefix (str): Route prefix of the server.
        endpoint (str): Endpoint to call.
        data (dict): Data to send to the endpoint.

    Returns:
        list: List of output chunks. If an error occurs, the list will contain
            only one element, which is the error response.
    """
    output = []
    r = requests.post(
        f"http://localhost:{port}{route_prefix}{endpoint}",
        data={"body": json.dumps(data)},
        timeout=30,
        stream=True,
    )
    for chunk in r.iter_content(chunk_size=None):
        chunk_output = json.loads(chunk.decode("utf-8"))
        output.append(chunk_output)
        if "error" in chunk_output:
            return [chunk_output]
    return output


def send_request_to_endpoint(
    port: int,
    route_prefix: str,
    endpoint_path: str,
    is_streaming: bool,
    data: dict,
) -> dict | list:
    """Call an endpoint.

    Args:
        target (str): the name of the target.
        port (int): Port of the server.
        route_prefix (str): Route prefix of the server.
        endpoint_path (str): Endpoint to call.
        is_streaming (bool): If True, the endpoint is a streaming endpoint.
        data (dict): Data to send to the endpoint.

    Returns:
        dict | list: Output of the endpoint. If the endpoint is a streaming endpoint, the output will be a list of output chunks.
            If the endpoint is not a streaming endpoint, the output will be a dict.
            If an error occurs, the output will be a dict with the error message.
    """
    if is_streaming:
        return call_streaming_endpoint(port, route_prefix, endpoint_path, data)
    else:
        r = requests.post(
            f"http://localhost:{port}{route_prefix}{endpoint_path}",
            data={"body": json.dumps(data)},
            timeout=30,
        )
        return r.json()


@pytest.fixture(scope="module")
def app_setup():
    """Setup Ray Serve app for given deployments and endpoints."""
    # create temporary database
    tmp_database_path = Path(tempfile.mkstemp(suffix=".db")[1])
    db_config = DbSettings(
        datastore_type=DbType.SQLITE,
        datastore_config=SQLiteConfig(path=tmp_database_path),
    )
    # set environment variable for the database config so Ray can find it
    os.environ["DB_CONFIG"] = jsonify(db_config)
    print(os.environ["DB_CONFIG"])
    # reload settings to update the database config
    import aana.configs.settings

    importlib.reload(aana.configs.settings)

    from aana_chat_with_video.app import aana_app

    aana_app.connect(
        port=8000, show_logs=True, num_cpus=10
    )  # pretend we have 10 cpus for testing

    def start_app():
        aana_app.migrate()
        aana_app.deploy()

        return aana_app

    yield start_app

    # delete temporary database
    tmp_database_path.unlink()

    aana_app.shutdown()


@pytest.fixture(scope="module")
def call_endpoint(app_setup):  # noqa: D417
    """Call endpoint.

    Args:
        endpoint_path: The endpoint path.
        data: The data to send.
        ignore_expected_output: Whether to ignore the expected output. Defaults to False.
        expected_error: The expected error. Defaults to None.
    """
    aana_app = app_setup()

    port = aana_app.port
    route_prefix = ""

    def _call_endpoint(
        endpoint_path: str,
        data: dict,
        ignore_expected_output: bool = False,
        expected_error: str | None = None,
    ) -> dict | list:
        endpoint = None
        for e in aana_app.endpoints.values():
            if e.path == endpoint_path:
                endpoint = e
                break
        if endpoint is None:
            raise ValueError(f"Endpoint with path {endpoint_path} not found")  # noqa: TRY003
        is_streaming = endpoint.is_streaming_response()

        return send_request_to_endpoint(
            port, route_prefix, endpoint_path, is_streaming, data
        )

    return _call_endpoint
