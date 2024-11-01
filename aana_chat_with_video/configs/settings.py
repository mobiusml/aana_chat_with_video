from aana.configs.settings import Settings as AanaSettings


class Settings(AanaSettings):
    """A pydantic model for App settings."""

    asr_model_name: str = "whisper_medium"
    captioning_model_name: str = "qwen2-vl-2b-instruct"
    max_video_len: int = 60 * 20  # 20 minutes


settings = Settings()
