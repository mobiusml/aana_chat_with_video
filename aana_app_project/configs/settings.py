from aana.configs.settings import Settings as AanaSettings


class Settings(AanaSettings):
    """A pydantic model for App settings."""
    # Add your custom settings here
    # Then, you can access them in your app like this:
    # from aana_app_project.configs.settings import settings
    # settings.custom_property
    pass


settings = Settings()
