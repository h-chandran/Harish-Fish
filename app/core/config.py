from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
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
    book_max_depth_ply: int = Field(default=24, alias="BOOK_MAX_DEPTH_PLY")
    stockfish_path: str | None = Field(default=None, alias="STOCKFISH_PATH")
    stockfish_threads: int = Field(default=1, alias="STOCKFISH_THREADS")
    stockfish_hash_mb: int = Field(default=128, alias="STOCKFISH_HASH_MB")
    stockfish_move_time_ms: int = Field(default=500, alias="STOCKFISH_MOVE_TIME_MS")
    stockfish_skill_level: int | None = Field(default=None, alias="STOCKFISH_SKILL_LEVEL")
    stockfish_limit_strength: bool = Field(default=True, alias="STOCKFISH_LIMIT_STRENGTH")

    @field_validator("stockfish_skill_level", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: object) -> int | None:
        if v == "" or v is None:
            return None
        return v
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
