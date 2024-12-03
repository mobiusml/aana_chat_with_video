from aana.configs.settings import Settings as AanaSettings


class Settings(AanaSettings):
    """A pydantic model for App settings."""

    asr_model_name: str = "whisper_medium"
    captioning_model_name: str = "hf_blip2_opt_2_7b"
    max_video_len: int = 60 * 20  # 20 minutes


settings = Settings()
