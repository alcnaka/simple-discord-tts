from pydantic import BaseSettings


class Settings(BaseSettings):
    DISCORD_TOKEN: str
    LISTEN_CHANNEL_ID: int
    VOICE_BACKEND_URL: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()  # type: ignore
