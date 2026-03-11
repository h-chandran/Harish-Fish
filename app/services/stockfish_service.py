from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import chess
import chess.engine


class StockfishConfigurationError(RuntimeError):
    """Raised when the local Stockfish binary is missing or unusable."""


@dataclass(frozen=True, slots=True)
class StockfishConfig:
    engine_path: Path | None
    threads: int = 1
    hash_mb: int = 128
    move_time_ms: int = 500
    skill_level: int | None = None
    limit_strength: bool = True
    elo: int = 2400


class StockfishService:
    """
    Wrapper around a local Stockfish UCI engine.

    The fallback strength is intentionally approximate. `LimitStrength=true` and
    `UCI_Elo=2400` provide a reasonable starting point, but practical playing
    strength will still vary by Stockfish build, hardware, and move time. We can
    calibrate these values later against your real games.
    """

    def __init__(self, config: StockfishConfig) -> None:
        self.config = config
        self._engine: chess.engine.SimpleEngine | None = None

    def is_configured(self) -> bool:
        return self.config.engine_path is not None

    def start(self) -> None:
        if self._engine is not None:
            return
        if self.config.engine_path is None:
            raise StockfishConfigurationError(
                "Stockfish binary is not configured. Set STOCKFISH_PATH to a valid executable."
            )
        if not self.config.engine_path.is_file():
            raise StockfishConfigurationError(
                f"Stockfish binary was not found at: {self.config.engine_path}"
            )

        try:
            self._engine = chess.engine.SimpleEngine.popen_uci(str(self.config.engine_path))
        except FileNotFoundError as exc:
            raise StockfishConfigurationError(
                f"Stockfish binary was not found at: {self.config.engine_path}"
            ) from exc
        except OSError as exc:
            raise StockfishConfigurationError(
                f"Failed to start Stockfish from: {self.config.engine_path}"
            ) from exc

        self._configure_engine()

    def close(self) -> None:
        if self._engine is not None:
            self._engine.quit()
            self._engine = None

    def get_best_move(self, board: chess.Board) -> chess.Move:
        if board.turn != chess.WHITE:
            raise ValueError("StockfishService is only used for White bot moves.")

        self.start()
        assert self._engine is not None
        result = self._engine.play(board, chess.engine.Limit(time=self.config.move_time_ms / 1000.0))
        if result.move is None:
            raise RuntimeError("Stockfish did not return a move.")
        return result.move

    def _configure_engine(self) -> None:
        assert self._engine is not None
        options: dict[str, int | bool] = {
            "Threads": self.config.threads,
            "Hash": self.config.hash_mb,
        }

        engine_options = self._engine.options
        if "Skill Level" in engine_options and self.config.skill_level is not None:
            options["Skill Level"] = self.config.skill_level
        if "UCI_LimitStrength" in engine_options:
            options["UCI_LimitStrength"] = self.config.limit_strength
        if "UCI_Elo" in engine_options and self.config.limit_strength:
            options["UCI_Elo"] = self.config.elo

        self._engine.configure(options)
