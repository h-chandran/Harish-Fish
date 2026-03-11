from __future__ import annotations

from pathlib import Path
import sys

import chess

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import get_settings
from app.services.book_controller import BookController, WhiteOpeningBook
from app.services.bot_move_service import BotMoveService
from app.services.stockfish_service import (
    StockfishConfig,
    StockfishConfigurationError,
    StockfishService,
)


def make_bot_service() -> BotMoveService:
    settings = get_settings()
    book = WhiteOpeningBook.load(Path(settings.generated_book_path))
    controller = BookController(book=book)
    stockfish = StockfishService(
        StockfishConfig(
            engine_path=Path(settings.stockfish_path).expanduser() if settings.stockfish_path else None,
            threads=settings.stockfish_threads,
            hash_mb=settings.stockfish_hash_mb,
            move_time_ms=settings.stockfish_move_time_ms,
            skill_level=settings.stockfish_skill_level,
            limit_strength=settings.stockfish_limit_strength,
            elo=settings.stockfish_elo,
        )
    )
    return BotMoveService(book_controller=controller, stockfish_service=stockfish)


def main() -> None:
    board = chess.Board()
    bot_service = make_bot_service()
    print("Human plays Black. Enter Black moves in UCI format such as e7e5 or g8f6.")
    print("Type 'quit' to exit.\n")

    try:
        while not board.is_game_over():
            if board.turn == chess.WHITE:
                result = bot_service.choose_white_move(board)
                board.push(result.move)
                print(f"Bot move ({result.source}): {result.move.uci()}")
                if result.book_decision is not None:
                    print(
                        f"  decision={result.book_decision.current_decision_number} "
                        f"probability={result.book_decision.probability_used:.1f} "
                        f"reason={result.book_decision.reason}"
                    )
                print(board)
                print()
                continue

            print(board)
            move_text = input("Black move> ").strip()
            if move_text.lower() == "quit":
                break

            try:
                move = chess.Move.from_uci(move_text)
            except ValueError:
                print("Invalid UCI format. Try a move like e7e5.\n")
                continue

            if move not in board.legal_moves:
                print("Illegal move for Black in the current position.\n")
                continue

            board.push(move)
            print()

        print(f"Game ended: {board.result(claim_draw=True)}")
    except StockfishConfigurationError as exc:
        print(f"Stockfish configuration error: {exc}")
    finally:
        bot_service.stockfish_service.close()


if __name__ == "__main__":
    main()
