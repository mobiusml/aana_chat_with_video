from pathlib import Path

from alembic import command
from alembic.config import Config

from aana.exceptions.runtime import EmptyMigrationsException


def get_alembic_config(
    app_config, ini_file_path: Path, alembic_data_path: Path
) -> Config:
    """Produces an alembic config to run migrations programmatically."""
    engine = app_config.db_config.get_engine()
    alembic_config = Config(ini_file_path)
    alembic_config.set_main_option("script_location", str(alembic_data_path))
    config_section = alembic_config.get_section(alembic_config.config_ini_section, {})
    config_section["sqlalchemy.url"] = engine.url

    return alembic_config


def run_alembic_migrations(settings):
    """Runs alembic migrations before starting up."""
    # We need the path to aana/alembic and aana/alembic.ini
    # This is a hack until we need something better.
    current_path = Path(__file__)
    aana_app_root = current_path.parent.parent  # go up two directories
    ini_file_path = aana_app_root / "alembic.ini"
    alembic_data_path = aana_app_root / "alembic"
    if not alembic_data_path.exists():
        raise RuntimeError("Alembic directory does not exist.")  # noqa: TRY003
    versions_path = alembic_data_path / "versions"
    # Check if the versions directory is empty (no .py files)
    if not versions_path.exists() or not any(Path(versions_path).glob("*.py")):
        raise EmptyMigrationsException()

    alembic_config = get_alembic_config(settings, ini_file_path, alembic_data_path)
    engine = settings.db_config.get_engine()
    with engine.begin() as connection:
        alembic_config.attributes["connection"] = connection
        command.upgrade(alembic_config, "head")


def drop_all_tables(settings):
    """Drops all tables in the database."""
    # TODO: only allow this in testing mode
    current_path = Path(__file__)
    aana_app_root = current_path.parent.parent  # go up two directories
    ini_file_path = aana_app_root / "alembic.ini"
    alembic_data_path = aana_app_root / "alembic"
    if not alembic_data_path.exists():
        raise RuntimeError("Alembic directory does not exist.")  # noqa: TRY003

    alembic_config = get_alembic_config(settings, ini_file_path, alembic_data_path)
    command.downgrade(alembic_config, "base")
