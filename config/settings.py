from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str

    RABBIT_HOST: str = 'localhost'
    RABBIT_PORT: int = 5672
    RABBIT_USER: str = 'guest'
    RABBIT_PASSWORD: str = 'guest'

    REDIS_HOST: str
    REDIS_PORT: str

    USER_RECOMMENDATIONS_QUEUE_TEMPLATE: str = 'user_recommendations.{user_id}'
    CHROMA_SETTINGS: dict = {
        'host': 'localhost',
        'port': 4810,
        'embedding_model': 'cointegrated/rubert-tiny2',
    }
    COLLECTION_NAME: str = 'users_collection'
    @property
    def rabbit_url(self) -> str:
        return f'amqp://{self.RABBIT_USER}:{self.RABBIT_PASSWORD}@{self.RABBIT_HOST}:{self.RABBIT_PORT}/'

    class Config:
        env_file = 'config/.env.example'


settings = Settings()
