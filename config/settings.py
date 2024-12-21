from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    BOT_WEBHOOK_URL: str

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    EMBEDDER_MODEL: str = 'cointegrated/rubert-tiny2'
    EMBEDDER_MODEL_DIMMENSION: int = 312

    RABBIT_HOST: str = 'localhost'
    RABBIT_PORT: int = 5672
    RABBIT_USER: str = 'guest'
    RABBIT_PASSWORD: str = 'guest'

    REDIS_HOST: str
    REDIS_PORT: str

    @property
    def rabbit_url(self) -> str:
        return f'amqp://{self.RABBIT_USER}:{self.RABBIT_PASSWORD}@{self.RABBIT_HOST}:{self.RABBIT_PORT}/'

    @property
    def db_uri(self) -> str:
        return f'{self.DB_NAME}://{self.DB_HOST}:{self.DB_PORT}'

    class Config:
        env_file = 'config/.env'


settings = Settings()