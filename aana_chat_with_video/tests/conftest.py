# ruff: noqa: S101
import os
import tempfile

import pytest
from sqlalchemy.orm import Session

from aana.configs.db import DbSettings, SQLiteConfig
from aana.configs.settings import settings as aana_settings
from aana.exceptions.runtime import EmptyMigrationsException
from aana.storage.op import DbType, run_alembic_migrations
from aana.tests.conftest import app_factory, call_endpoint  # noqa: F401
from aana.utils.json import jsonify
from aana_chat_with_video.configs.settings import settings
from aana_chat_with_video.storage.op import (
    run_alembic_migrations as run_app_alembic_migrations,
)


@pytest.fixture(scope="function")
def db_session():
    """Creates a new database file and session for each test."""
    with tempfile.NamedTemporaryFile(dir=settings.tmp_data_dir) as tmp:
        db_config = DbSettings(
            datastore_type=DbType.SQLITE,
            datastore_config=SQLiteConfig(path=tmp.name),
        )
        os.environ["DB_CONFIG"] = jsonify(db_config)

        settings.db_config = db_config
        settings.db_config._engine = None
        aana_settings.db_config = db_config
        aana_settings.db_config._engine = None

        try:
            run_app_alembic_migrations(settings)
        except EmptyMigrationsException:
            print(
                "No versions found in the custom migrations. Using default migrations."
            )
            run_alembic_migrations(settings)

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
