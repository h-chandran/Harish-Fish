import json
from pathlib import Path

import chess

from app.services.book_controller import BookController, WhiteOpeningBook
from app.services.bot_move_service import BotMoveService


class FakeRng:
    def __init__(self, rolls: list[float] | None = None, chosen_indices: list[int] | None = None) -> None:
        self.rolls = rolls or []
        self.chosen_indices = chosen_indices or []

    def random(self) -> float:
        if not self.rolls:
            raise AssertionError("No random roll configured.")
        return self.rolls.pop(0)

    def choices(self, population: list[str], weights: list[float], k: int = 1) -> list[str]:
        if not self.chosen_indices:
            return [population[0]]
        return [population[self.chosen_indices.pop(0)]]


class FakeStockfishService:
    def __init__(self, moves: list[str]) -> None:
        self.moves = moves
        self.calls = 0

    def get_best_move(self, board: chess.Board) -> chess.Move:
        self.calls += 1
        if not self.moves:
            raise AssertionError("No fake Stockfish move configured.")
        return chess.Move.from_uci(self.moves.pop(0))


def make_book(tmp_path: Path, positions: dict[str, list[dict[str, float]]]) -> WhiteOpeningBook:
    book_path = tmp_path / "white_opening_book.json"
    payload = {
        "metadata": {
            "name": "White Repertoire Book",
            "max_depth_ply": 24,
            "side": "white",
            "source_file": "data/repertoire_db/master_repertoire.pgn",
        },
        "positions": {fen: {"moves": moves} for fen, moves in positions.items()},
    }
    book_path.write_text(json.dumps(payload), encoding="utf-8")
    return WhiteOpeningBook.load(book_path)


def test_repertoire_move_chosen_when_available_and_accepted(tmp_path: Path) -> None:
    start_fen = chess.Board().fen()
    book = make_book(tmp_path, {start_fen: [{"uci": "e2e4", "weight": 1.0}]})
    controller = BookController(book=book, rng=FakeRng(rolls=[0.0], chosen_indices=[0]))
    stockfish = FakeStockfishService(moves=["d2d4"])
    service = BotMoveService(book_controller=controller, stockfish_service=stockfish)

    result = service.choose_white_move(chess.Board())

    assert result.source == "book"
    assert result.move == chess.Move.from_uci("e2e4")
    assert result.book_decision is not None
    assert result.book_decision.reason == "book_move_played"
    assert stockfish.calls == 0


def test_stockfish_used_when_out_of_book(tmp_path: Path) -> None:
    book = make_book(tmp_path, {})
    controller = BookController(book=book, rng=FakeRng())
    stockfish = FakeStockfishService(moves=["e2e4"])
    service = BotMoveService(book_controller=controller, stockfish_service=stockfish)

    result = service.choose_white_move(chess.Board())

    assert result.source == "stockfish"
    assert result.move == chess.Move.from_uci("e2e4")
    assert result.book_decision is not None
    assert result.book_decision.reason == "book_miss"
    assert controller.in_book is False
    assert stockfish.calls == 1


def test_game_state_maintained_correctly_across_multiple_plies(tmp_path: Path) -> None:
    start_board = chess.Board()
    after_e4_e5 = chess.Board()
    after_e4_e5.push_uci("e2e4")
    after_e4_e5.push_uci("e7e5")
    after_fallback_position = chess.Board()
    after_fallback_position.push_uci("e2e4")
    after_fallback_position.push_uci("e7e5")
    after_fallback_position.push_uci("f1b5")
    after_fallback_position.push_uci("b8c6")

    book = make_book(
        tmp_path,
        {
            start_board.fen(): [{"uci": "e2e4", "weight": 1.0}],
            after_e4_e5.fen(): [{"uci": "g1f3", "weight": 1.0}],
        },
    )
    controller = BookController(book=book, rng=FakeRng(rolls=[0.0, 0.95], chosen_indices=[0]))
    stockfish = FakeStockfishService(moves=["f1b5", "d2d3"])
    service = BotMoveService(book_controller=controller, stockfish_service=stockfish)

    first = service.choose_white_move(start_board)
    start_board.push(first.move)
    start_board.push_uci("e7e5")

    second = service.choose_white_move(start_board)
    start_board.push(second.move)
    start_board.push_uci("b8c6")

    third = service.choose_white_move(start_board)

    assert first.source == "book"
    assert first.move == chess.Move.from_uci("e2e4")
    assert second.source == "stockfish"
    assert second.book_decision is not None
    assert second.book_decision.reason == "declined_book"
    assert controller.in_book is False
    assert controller.white_repertoire_decisions_made == 1
    assert third.source == "stockfish"
    assert third.move == chess.Move.from_uci("d2d3")
    assert third.book_decision is not None
    assert third.book_decision.reason == "already_out_of_book"
    assert stockfish.calls == 2
    assert start_board.fen() == after_fallback_position.fen()
