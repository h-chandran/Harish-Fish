from __future__ import annotations

from dataclasses import dataclass

import chess

from app.services.book_controller import BookController, BookDecision
from app.services.stockfish_service import StockfishService


@dataclass(frozen=True, slots=True)
class BotMoveResult:
    move: chess.Move
    source: str
    book_decision: BookDecision | None = None


class BotMoveService:
    """Choose White moves from repertoire first, then fall back to Stockfish."""

    def __init__(self, book_controller: BookController, stockfish_service: StockfishService) -> None:
        self.book_controller = book_controller
        self.stockfish_service = stockfish_service

    def choose_white_move(self, board: chess.Board) -> BotMoveResult:
        if board.turn != chess.WHITE:
            raise ValueError("BotMoveService only supports choosing moves for White.")

        book_decision = self.book_controller.choose_book_move(board.fen())
        if book_decision.chosen_move:
            return BotMoveResult(
                move=chess.Move.from_uci(book_decision.chosen_move),
                source="book",
                book_decision=book_decision,
            )

        move = self.stockfish_service.get_best_move(board)
        return BotMoveResult(move=move, source="stockfish", book_decision=book_decision)
