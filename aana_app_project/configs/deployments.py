deployments: list[dict] = []

# Add deployments for models that you want to deploy here.
#
# For example:
# from aana.deployments.whisper_deployment import (
#     WhisperComputeType,
#     WhisperConfig,
#     WhisperDeployment,
#     WhisperModelSize,
# )
# asr_deployment = WhisperDeployment.options(
#     num_replicas=1,
#     ray_actor_options={"num_gpus": 0.1},
#     user_config=WhisperConfig(
#         model_size=WhisperModelSize.MEDIUM,
#         compute_type=WhisperComputeType.FLOAT16,
#     ).model_dump(mode="json"),
# )
# deployments.append({"name": "asr_deployment", "instance": asr_deployment})
#
# You can use predefined deployments from the Aana SDK or create your own.
# See https://github.com/mobiusml/aana_sdk/blob/main/docs/integrations.md for the list of predefined deployments.
#
# If you want to create your own deployment, put your deployment classes in a separate files in the `deployments` directory and import them here.
