from aana.core.models.sampling import SamplingParams
from aana.core.models.types import Dtype
from aana.deployments.vad_deployment import VadConfig, VadDeployment
from aana.deployments.hf_blip2_deployment import HFBlip2Config, HFBlip2Deployment
from aana.deployments.vllm_deployment import VLLMConfig, VLLMDeployment
from aana.deployments.whisper_deployment import (
    WhisperComputeType,
    WhisperConfig,
    WhisperDeployment,
    WhisperModelSize,
)

deployments: list[dict] = [
    {
        "name": "asr_deployment",
        "instance": WhisperDeployment.options(
            num_replicas=1,
            max_ongoing_requests=1000,
            ray_actor_options={"num_gpus": 0.25},
            user_config=WhisperConfig(
                model_size=WhisperModelSize.TURBO,
                compute_type=WhisperComputeType.FLOAT16,
            ).model_dump(mode="json"),
        ),
    },
    {
        "name": "vad_deployment",
        "instance": VadDeployment.options(
            num_replicas=1,
            max_ongoing_requests=1000,
            ray_actor_options={"num_gpus": 0.05},
            user_config=VadConfig(
                model=(
                    "https://whisperx.s3.eu-west-2.amazonaws.com/model_weights/segmentation/"
                    "0b5b3216d60a2d32fc086b47ea8c67589aaeb26b7e07fcbe620d6d0b83e209ea/pytorch_model.bin"
                ),
                onset=0.5,
                sample_rate=16000,
            ).model_dump(mode="json"),
        ),
    },
    {
        "name": "captioning_deployment",
        "instance": HFBlip2Deployment.options(
            num_replicas=1,
            max_ongoing_requests=1000,
            ray_actor_options={"num_gpus": 0.25},
            user_config=HFBlip2Config(
                model="Salesforce/blip2-opt-2.7b",
                dtype=Dtype.FLOAT16,
                batch_size=2,
                num_processing_threads=2,
            ).model_dump(mode="json"),
        ),
    },
    {
        "name": "llm_deployment",
        "instance": VLLMDeployment.options(
            num_replicas=1,
            ray_actor_options={"num_gpus": 0.45},
            user_config=VLLMConfig(
                model="internlm/internlm2_5-7b-chat",
                dtype=Dtype.AUTO,
                gpu_memory_reserved=30000,
                max_model_len=50000,
                enforce_eager=True,
                default_sampling_params=SamplingParams(
                    temperature=0.0, top_p=1.0, top_k=-1, max_tokens=1024
                ),
                engine_args={"trust_remote_code": True},
            ).model_dump(mode="json"),
        ),
    },
]
