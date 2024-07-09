from aana.configs.settings import Settings as AanaSettings


class Settings(AanaSettings):
    """A pydantic model for App settings."""
    # Add your custom settings here
    # Then, you can access them in your app like this:
    # from aana_chat_with_video.configs.settings import settings
    # settings.custom_property
    pass


settings = Settings()
