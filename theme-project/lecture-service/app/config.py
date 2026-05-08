from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_conf = SettingsConfigDict(env_file='.env', extra='ignore')

    DATABASE_URL: str
    GIGACHAT_API: str
    GIGACHAT_SCOPE: str

settings = Settings()

