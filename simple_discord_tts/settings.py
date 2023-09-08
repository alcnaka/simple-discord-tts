from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DISCORD_TOKEN: str
    LISTEN_CHANNEL_ID: int
    VOICE_BACKEND_URL: str

    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type: ignore[reportGeneralTypeIssue]
