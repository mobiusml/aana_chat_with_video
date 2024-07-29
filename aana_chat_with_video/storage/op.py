from aana.storage.op import run_alembic_migrations as run_alembic_migrations_aana
from aana.utils.core import get_module_dir


def run_alembic_migrations(settings):
    """Runs alembic migrations before starting up."""
    root_path = get_module_dir("aana_chat_with_video")

    run_alembic_migrations_aana(settings, root_path)
