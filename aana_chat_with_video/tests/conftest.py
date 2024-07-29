# ruff: noqa: S101
import importlib
import os
import tempfile
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from aana.configs.db import DbSettings, SQLiteConfig
from aana.exceptions.runtime import EmptyMigrationsException
from aana.storage.op import DbType
from aana.utils.json import jsonify
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
    engine = settings.db_config.get_engine()
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="module")
def app_setup(app_factory):
    """Setup app for testing."""
    app, tmp_database_path = app_factory("aana_chat_with_video.app", "aana_app")
    yield app
    tmp_database_path.unlink()
    app.shutdown()
