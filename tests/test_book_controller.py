import json
from pathlib import Path

import chess

from app.services.book_controller import BookController, WhiteOpeningBook


class FakeRng:
    def __init__(self, rolls: list[float] | None = None, chosen_indices: list[int] | None = None) -> None:
        self.rolls = rolls or []
        self.chosen_indices = chosen_indices or []

    def random(self) -> float:
        if not self.rolls:
            raise AssertionError("No random roll configured.")
        return self.rolls.pop(0)

    def choices(self, population: list[str], weights: list[float], k: int = 1) -> list[str]:
        if k != 1:
            raise AssertionError("FakeRng only supports k=1.")
        if not self.chosen_indices:
            return [population[0]]
        index = self.chosen_indices.pop(0)
        return [population[index]]


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


def test_exact_probability_schedule() -> None:
    probabilities = [BookController.probability_for_decision(index) for index in range(1, 14)]

    assert probabilities == [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0, 0.0, 0.0]


def test_permanent_exit_after_declining_book(tmp_path: Path) -> None:
    start_fen = chess.Board().fen()
    book = make_book(
        tmp_path,
        {
            start_fen: [
                {"uci": "e2e4", "weight": 3.0},
                {"uci": "d2d4", "weight": 1.0},
            ]
        },
    )
    controller = BookController(book=book, rng=FakeRng(rolls=[1.0]))

    declined = controller.choose_book_move(start_fen)
    after_decline = controller.choose_book_move(start_fen)

    assert declined.reason == "declined_book"
    assert declined.in_book_after is False
    assert declined.probability_used == 1.0
    assert controller.white_repertoire_decisions_made == 0
    assert after_decline.reason == "already_out_of_book"
    assert after_decline.in_book_after is False
    assert after_decline.probability_used == 0.0


def test_permanent_exit_after_book_miss(tmp_path: Path) -> None:
    book = make_book(tmp_path, {})
    controller = BookController(book=book, rng=FakeRng())
    start_fen = chess.Board().fen()

    missed = controller.choose_book_move(start_fen)
    after_miss = controller.choose_book_move(start_fen)

    assert missed.reason == "book_miss"
    assert missed.in_book_after is False
    assert missed.probability_used == 1.0
    assert controller.white_repertoire_decisions_made == 0
    assert after_miss.reason == "already_out_of_book"


def test_weighted_move_selection_uses_available_book_moves(tmp_path: Path) -> None:
    start_fen = chess.Board().fen()
    book = make_book(
        tmp_path,
        {
            start_fen: [
                {"uci": "e2e4", "weight": 3.0},
                {"uci": "d2d4", "weight": 1.0},
            ]
        },
    )
    controller = BookController(book=book, rng=FakeRng(rolls=[0.0], chosen_indices=[1]))

    decision = controller.choose_book_move(start_fen)

    assert decision.reason == "book_move_played"
    assert decision.chosen_move == "d2d4"
    assert [move.uci for move in decision.available_moves] == ["e2e4", "d2d4"]
    assert [move.weight for move in decision.available_moves] == [3.0, 1.0]


def test_white_repertoire_decision_counting_only_increments_on_played_book_move(tmp_path: Path) -> None:
    start_fen = chess.Board().fen()
    after_e4_e5 = chess.Board()
    after_e4_e5.push_uci("e2e4")
    after_e4_e5.push_uci("e7e5")

    book = make_book(
        tmp_path,
        {
            start_fen: [{"uci": "e2e4", "weight": 1.0}],
            after_e4_e5.fen(): [{"uci": "g1f3", "weight": 1.0}],
        },
    )
    controller = BookController(book=book, rng=FakeRng(rolls=[0.0, 0.95], chosen_indices=[0]))

    first = controller.choose_book_move(start_fen)
    second = controller.choose_book_move(after_e4_e5.fen())
    third = controller.choose_book_move(after_e4_e5.fen())

    assert first.current_decision_number == 1
    assert first.probability_used == 1.0
    assert first.chosen_move == "e2e4"
    assert controller.white_repertoire_decisions_made == 1

    assert second.current_decision_number == 2
    assert second.probability_used == 0.9
    assert second.reason == "declined_book"
    assert controller.white_repertoire_decisions_made == 1

    assert third.reason == "already_out_of_book"
    assert third.current_decision_number == 2
