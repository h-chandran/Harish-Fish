from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


class RandomLike(Protocol):
    def random(self) -> float: ...

    def choices(self, population: list[str], weights: list[float], k: int = 1) -> list[str]: ...


@dataclass(frozen=True, slots=True)
class BookMove:
    uci: str
    weight: float


@dataclass(frozen=True, slots=True)
class WhiteOpeningBook:
    metadata: dict
    positions: dict[str, tuple[BookMove, ...]]

    @classmethod
    def load(cls, book_path: Path) -> "WhiteOpeningBook":
        payload = json.loads(book_path.read_text(encoding="utf-8"))
        positions = {
            fen: tuple(
                BookMove(uci=move["uci"], weight=float(move["weight"]))
                for move in entry.get("moves", [])
            )
            for fen, entry in payload.get("positions", {}).items()
        }
        return cls(metadata=payload.get("metadata", {}), positions=positions)

    def get_moves(self, fen: str) -> tuple[BookMove, ...]:
        return self.positions.get(fen, ())


@dataclass(slots=True)
class BookDecision:
    fen: str
    in_book_before: bool
    in_book_after: bool
    current_decision_number: int
    probability_used: float
    chosen_move: str | None = None
    reason: str = "out_of_book"
    available_moves: tuple[BookMove, ...] = field(default_factory=tuple)


class BookController:
    """Runtime controller for White opening-book usage and permanent out-of-book transitions."""

    def __init__(self, book: WhiteOpeningBook, rng: RandomLike | None = None) -> None:
        self.book = book
        self.rng = rng or random.Random()
        self.in_book = True
        self.white_repertoire_decisions_made = 0

    @staticmethod
    def probability_for_decision(decision_number: int) -> float:
        return round(max(0.0, 1.0 - 0.1 * (decision_number - 1)), 10)

    @property
    def current_decision_number(self) -> int:
        return self.white_repertoire_decisions_made + 1

    def choose_book_move(self, fen: str) -> BookDecision:
        decision_number = self.current_decision_number
        probability = self.probability_for_decision(decision_number)
        in_book_before = self.in_book

        if not self.in_book:
            return BookDecision(
                fen=fen,
                in_book_before=in_book_before,
                in_book_after=False,
                current_decision_number=decision_number,
                probability_used=0.0,
                reason="already_out_of_book",
            )

        moves = self.book.get_moves(fen)
        if not moves:
            self.in_book = False
            return BookDecision(
                fen=fen,
                in_book_before=in_book_before,
                in_book_after=False,
                current_decision_number=decision_number,
                probability_used=probability,
                reason="book_miss",
            )

        if self.rng.random() >= probability:
            self.in_book = False
            return BookDecision(
                fen=fen,
                in_book_before=in_book_before,
                in_book_after=False,
                current_decision_number=decision_number,
                probability_used=probability,
                reason="declined_book",
                available_moves=moves,
            )

        chosen_move = self._select_weighted_move(moves)
        self.white_repertoire_decisions_made += 1
        return BookDecision(
            fen=fen,
            in_book_before=in_book_before,
            in_book_after=True,
            current_decision_number=decision_number,
            probability_used=probability,
            chosen_move=chosen_move.uci,
            reason="book_move_played",
            available_moves=moves,
        )

    def _select_weighted_move(self, moves: tuple[BookMove, ...]) -> BookMove:
        population = [move.uci for move in moves]
        weights = [move.weight for move in moves]
        chosen_uci = self.rng.choices(population=population, weights=weights, k=1)[0]
        for move in moves:
            if move.uci == chosen_uci:
                return move
        raise RuntimeError(f"Weighted selection returned unknown move: {chosen_uci}")
