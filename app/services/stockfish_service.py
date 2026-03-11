from pathlib import Path


class StockfishService:
    """Placeholder wrapper around a local Stockfish process."""

    def __init__(self, engine_path: str | None, target_elo: int = 2400) -> None:
        self.engine_path = Path(engine_path).expanduser() if engine_path else None
        self.target_elo = target_elo

    def is_configured(self) -> bool:
        """Return whether a Stockfish binary path has been configured."""
        return self.engine_path is not None

    def get_move(self, fen: str) -> str:
        """Return an engine move for the given position."""
        raise NotImplementedError("Stockfish integration is not implemented yet.")
