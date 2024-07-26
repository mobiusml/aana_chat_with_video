from aana.sdk import AanaSDK
from aana_chat_with_video.configs.deployments import deployments
from aana_chat_with_video.configs.endpoints import endpoints
from aana_chat_with_video.storage.op import run_alembic_migrations

aana_app = AanaSDK(name="aana_chat_with_video", migration_func=run_alembic_migrations)

for deployment in deployments:
    aana_app.register_deployment(**deployment)

for endpoint in endpoints:
    aana_app.register_endpoint(**endpoint)

if __name__ == "__main__":
    aana_app.connect()
    aana_app.migrate()
    aana_app.deploy()
