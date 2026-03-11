from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.core.config import get_settings
from app.services.book_controller import BookController, WhiteOpeningBook
from app.services.bot_move_service import BotMoveService
from app.services.game_manager import GameSessionManager
from app.services.stockfish_service import StockfishConfig, StockfishService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown wiring for reusable runtime services."""
    settings = get_settings()
    app.state.services_ready = False
    app.state.opening_book = None
    app.state.book_controller = None
    app.state.stockfish_service = None
    app.state.bot_move_service = None
    app.state.session_manager = None

    if settings.generated_book_path.is_file():
        app.state.opening_book = WhiteOpeningBook.load(settings.generated_book_path)
        app.state.book_controller = BookController(book=app.state.opening_book)
    else:
        app.state.opening_book = WhiteOpeningBook(metadata={}, positions={})
        app.state.book_controller = BookController(book=app.state.opening_book)

    stockfish_service = StockfishService(
        config=StockfishConfig(
            engine_path=Path(settings.stockfish_path).expanduser() if settings.stockfish_path else None,
            threads=settings.stockfish_threads,
            hash_mb=settings.stockfish_hash_mb,
            move_time_ms=settings.stockfish_move_time_ms,
            skill_level=settings.stockfish_skill_level,
            limit_strength=settings.stockfish_limit_strength,
            elo=settings.stockfish_elo,
        )
    )
    app.state.stockfish_service = stockfish_service

    if app.state.book_controller is not None:
        app.state.bot_move_service = BotMoveService(
            book_controller=app.state.book_controller,
            stockfish_service=stockfish_service,
        )
        app.state.session_manager = GameSessionManager(
            opening_book=app.state.opening_book,
            stockfish_service=stockfish_service,
        )

    # We only warm the engine if a binary path is configured. If the path is
    # missing or invalid, runtime callers will receive a clear configuration error.
    if stockfish_service.is_configured():
        try:
            stockfish_service.start()
        except Exception:
            stockfish_service.close()

    app.state.services_ready = True

    try:
        yield
    finally:
        if app.state.stockfish_service is not None:
            app.state.stockfish_service.close()
        app.state.services_ready = False
