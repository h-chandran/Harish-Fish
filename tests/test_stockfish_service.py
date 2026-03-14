import sys
from pathlib import Path

import chess
import pytest

from app.services.stockfish_service import (
    StockfishConfig,
    StockfishConfigurationError,
    StockfishService,
)


def test_stockfish_service_raises_clear_error_for_missing_binary() -> None:
    service = StockfishService(StockfishConfig(engine_path=Path("C:/missing/stockfish.exe")))

    with pytest.raises(StockfishConfigurationError):
        service.start()


def test_stockfish_service_can_get_move_via_python_chess_engine_integration(tmp_path: Path) -> None:
    fixture_path = Path(__file__).resolve().parent / "fixtures" / "fake_uci_engine.py"
    wrapper_path = tmp_path / "fake_uci_engine.cmd"
    wrapper_path.write_text(
        f'@echo off\r\n"{sys.executable}" "{fixture_path}"\r\n',
        encoding="utf-8",
    )

    service = StockfishService(
        StockfishConfig(
            engine_path=wrapper_path,
            threads=1,
            hash_mb=32,
            move_time_ms=100,
            skill_level=18,
            limit_strength=True,
            elo=2400,
        )
    )

    move = service.get_best_move(chess.Board())
    service.close()

    assert isinstance(move, chess.Move)
    assert service.is_ready is False
