from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = Field(default="Harish Fish", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="127.0.0.1", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    debug: bool = Field(default=True, alias="DEBUG")
    allowed_origins: list[str] = Field(
        default=["http://127.0.0.1:8000", "http://localhost:8000"],
        alias="ALLOWED_ORIGINS",
    )
    master_pgn_path: Path = Field(
        default=BASE_DIR / "data" / "repertoire_db" / "master_repertoire.pgn",
        alias="MASTER_PGN_PATH",
    )
    generated_book_path: Path = Field(
        default=BASE_DIR / "data" / "generated" / "white_opening_book.json",
        alias="GENERATED_BOOK_PATH",
    )
    stockfish_path: str | None = Field(default=None, alias="STOCKFISH_PATH")
    stockfish_skill_level: int = Field(default=18, alias="STOCKFISH_SKILL_LEVEL")
    stockfish_elo: int = Field(default=2400, alias="STOCKFISH_ELO")
    book_decay_percent: int = Field(default=10, alias="BOOK_DECAY_PERCENT")
    book_min_probability: int = Field(default=0, alias="BOOK_MIN_PROBABILITY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
