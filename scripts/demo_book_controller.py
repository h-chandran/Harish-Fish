from __future__ import annotations

from pathlib import Path
import sys

import chess

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import get_settings
from app.services.book_controller import BookController, WhiteOpeningBook


def main() -> None:
    settings = get_settings()
    book = WhiteOpeningBook.load(Path(settings.generated_book_path))
    controller = BookController(book=book)
    current_fen = chess.Board().fen()
    decision = controller.choose_book_move(current_fen)

    print(f"Current FEN: {decision.fen}")
    print(f"Current White repertoire decision number: {decision.current_decision_number}")
    print(f"Probability used: {decision.probability_used:.1f}")
    if decision.chosen_move:
        print(f"Chosen book move: {decision.chosen_move}")
    else:
        print("Chosen book move: none")
    print(f"Reason: {decision.reason}")
    print(f"In book after decision: {decision.in_book_after}")


if __name__ == "__main__":
    main()
