from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

import chess

from app.services.book_controller import BookController, WhiteOpeningBook
from app.services.bot_move_service import BotMoveResult, BotMoveService
from app.services.stockfish_service import StockfishService


class GameSessionError(RuntimeError):
    """Base error for invalid or missing game sessions."""


class SessionNotFoundError(GameSessionError):
    """Raised when a game ID is unknown."""


class InvalidMoveError(GameSessionError):
    """Raised when a move is invalid for the current position or side."""


@dataclass(slots=True)
class GameSession:
    game_id: str
    board: chess.Board
    book_controller: BookController

    @property
    def in_book(self) -> bool:
        return self.book_controller.in_book

    @property
    def white_repertoire_decisions_made(self) -> int:
        return self.book_controller.white_repertoire_decisions_made


class GameSessionManager:
    """Simple in-memory session manager for local testing."""

    def __init__(self, opening_book: WhiteOpeningBook, stockfish_service: StockfishService) -> None:
        self.opening_book = opening_book
        self.stockfish_service = stockfish_service
        self.sessions: dict[str, GameSession] = {}

    def create_session(self, bot_move_first: bool = False) -> tuple[GameSession, BotMoveResult | None]:
        session = self._new_session()
        self.sessions[session.game_id] = session
        bot_result = self.make_bot_move(session.game_id) if bot_move_first else None
        return session, bot_result

    def apply_player_move(self, game_id: str, move_uci: str) -> GameSession:
        session = self.get_session(game_id)
        if session.board.turn != chess.BLACK:
            raise InvalidMoveError("It is not Black's turn.")

        try:
            move = chess.Move.from_uci(move_uci)
        except ValueError as exc:
            raise InvalidMoveError("Move must be valid UCI.") from exc

        if move not in session.board.legal_moves:
            raise InvalidMoveError("Move is illegal in the current position.")

        session.board.push(move)
        return session

    def make_bot_move(self, game_id: str) -> BotMoveResult:
        session = self.get_session(game_id)
        if session.board.turn != chess.WHITE:
            raise InvalidMoveError("It is not White's turn.")

        service = BotMoveService(
            book_controller=session.book_controller,
            stockfish_service=self.stockfish_service,
        )
        result = service.choose_white_move(session.board)
        session.board.push(result.move)
        return result

    def reset_session(self, game_id: str, bot_move_first: bool = False) -> tuple[GameSession, BotMoveResult | None]:
        if game_id not in self.sessions:
            raise SessionNotFoundError(f"Unknown game_id: {game_id}")

        session = self._new_session(game_id=game_id)
        self.sessions[game_id] = session
        bot_result = self.make_bot_move(game_id) if bot_move_first else None
        return session, bot_result

    def get_session(self, game_id: str) -> GameSession:
        session = self.sessions.get(game_id)
        if session is None:
            raise SessionNotFoundError(f"Unknown game_id: {game_id}")
        return session

    def _new_session(self, game_id: str | None = None) -> GameSession:
        return GameSession(
            game_id=game_id or str(uuid4()),
            board=chess.Board(),
            book_controller=BookController(book=self.opening_book),
        )
