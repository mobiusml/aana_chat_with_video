# ruff: noqa: S101
import importlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import pytest
import requests
from aana.api.api_generation import Endpoint
from aana.configs.db import DbSettings, SQLiteConfig
from aana.exceptions.runtime import EmptyMigrationsException
from aana.sdk import AanaSDK
from aana.storage.op import DbType
from aana.storage.session import get_session
from aana.utils.json import jsonify
from pydantic import ValidationError

from aana_chat_with_video.storage.op import (
    run_alembic_migrations as run_app_alembic_migrations,
)


@pytest.fixture(scope="function")
def db_session():
    """Creates a new database file and session for each test."""
    tmp_database_path = Path(tempfile.mkstemp(suffix=".db")[1])
    db_config = DbSettings(
        datastore_type=DbType.SQLITE,
        datastore_config=SQLiteConfig(path=tmp_database_path),
    )
    os.environ["DB_CONFIG"] = jsonify(db_config)

    # Reload the settings to update the database path
    import aana.configs.settings

    import aana_chat_with_video.configs.settings

    importlib.reload(aana.configs.settings)
    importlib.reload(aana_chat_with_video.configs.settings)

    from aana_chat_with_video.configs.settings import settings

    # Run migrations to set up the schema
    try:
        run_app_alembic_migrations(settings)
    except EmptyMigrationsException:
        print("No versions found in the custom migrations. Using default migrations.")
        run_app_alembic_migrations(settings)

    # Create a new session
    with get_session() as session:
        yield session


def send_api_request(
    endpoint: Endpoint,
    app: AanaSDK,
    data: dict[str, Any],
    timeout: int = 30,
) -> dict[str, Any] | list[dict[str, Any]]:
    """Call an endpoint, handling both streaming and non-streaming responses."""
    url = f"http://localhost:{app.port}{endpoint.path}"
    payload = {"body": json.dumps(data)}

    if endpoint.is_streaming_response():
        output = []
        with requests.post(url, data=payload, timeout=timeout, stream=True) as r:
            for chunk in r.iter_content(chunk_size=None):
                chunk_output = json.loads(chunk.decode("utf-8"))
                output.append(chunk_output)
                if "error" in chunk_output:
                    return [chunk_output]
        return output
    else:
        response = requests.post(url, data=payload, timeout=timeout)
        return response.json()


def verify_output(
    endpoint: Endpoint,
    response: dict[str, Any] | list[dict[str, Any]],
    expected_error: str | None = None,
) -> None:
    """Verify the output of an endpoint call."""
    is_streaming = endpoint.is_streaming_response()
    ResponseModel = endpoint.get_response_model()
    if expected_error:
        error = response[0]["error"] if is_streaming else response["error"]
        assert error == expected_error, response
    else:
        try:
            if is_streaming:
                for item in response:
                    ResponseModel.model_validate(item, strict=True)
            else:
                ResponseModel.model_validate(response, strict=True)
        except ValidationError as e:
            raise AssertionError(  # noqa: TRY003
                f"Validation failed. Errors:\n{e}\n\nResponse: {response}"
            ) from e


@pytest.fixture(scope="module")
def app_setup():
    """Setup Ray Serve app for testing."""
    # Create a temporary database for testing
    tmp_database_path = Path(tempfile.mkstemp(suffix=".db")[1])
    db_config = DbSettings(
        datastore_type=DbType.SQLITE,
        datastore_config=SQLiteConfig(path=tmp_database_path),
    )
    os.environ["DB_CONFIG"] = jsonify(db_config)

    # Reload the settings to update the database path
    import aana.configs.settings

    importlib.reload(aana.configs.settings)

    # Start the app
    from aana_chat_with_video.app import aana_app

    aana_app.connect(port=8000, show_logs=True, num_cpus=10)
    aana_app.migrate()
    aana_app.deploy()

    yield aana_app

    tmp_database_path.unlink()
    aana_app.shutdown()


@pytest.fixture(scope="module")
def call_endpoint(app_setup):
    """Call an endpoint and verify the output."""
    aana_app: AanaSDK = app_setup

    def _call_endpoint(
        endpoint_path: str,
        data: dict[str, Any],
        expected_error: str | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        endpoint = next(
            (e for e in aana_app.endpoints.values() if e.path == endpoint_path), None
        )
        if endpoint is None:
            raise ValueError(f"Endpoint with path {endpoint_path} not found")  # noqa: TRY003

        response = send_api_request(endpoint=endpoint, app=aana_app, data=data)
        verify_output(
            endpoint=endpoint,
            response=response,
            expected_error=expected_error,
        )

        return response

    return _call_endpoint
