from pydantic_settings import BaseSettings, SettingsConfigDict
from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(token=env("BOT_TOKEN"))
    )

class Settings(BaseSettings):
    DB_HOST: str  # Хост базы данных.
    DB_PORT: int  # Порт базы данных.
    DB_USER: str  # Имя пользователя базы данных.
    DB_PASS: str  # Пароль пользователя базы данных.
    DB_NAME: str  # Имя базы данных.
    BOT_TOKEN: str  # Токен бота.

    @property
    def database_url_asyncpg(self):
        # Возвращаем URL для подключения к базе данных с использованием драйвера psycopg2.
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()