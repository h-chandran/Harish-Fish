import json
from pathlib import Path

import chess
from fastapi.testclient import TestClient

from app.main import create_app
from app.services.book_controller import WhiteOpeningBook
from app.services.game_manager import GameSessionManager


class FakeStockfishService:
    def __init__(self, moves: list[str]) -> None:
        self.moves = moves
        self.is_ready = True

    def get_best_move(self, board: chess.Board) -> chess.Move:
        return chess.Move.from_uci(self.moves.pop(0))

    def close(self) -> None:
        return None


def make_book(tmp_path: Path) -> WhiteOpeningBook:
    start_board = chess.Board()
    after_e4_e5 = chess.Board()
    after_e4_e5.push_uci("e2e4")
    after_e4_e5.push_uci("e7e5")
    payload = {
        "metadata": {
            "name": "White Repertoire Book",
            "max_depth_ply": 24,
            "side": "white",
            "source_file": "data/repertoire_db/master_repertoire.pgn",
        },
        "positions": {
            start_board.fen(): {"moves": [{"uci": "e2e4", "weight": 1.0}]},
            after_e4_e5.fen(): {"moves": [{"uci": "g1f3", "weight": 1.0}]},
        },
    }
    book_path = tmp_path / "white_opening_book.json"
    book_path.write_text(json.dumps(payload), encoding="utf-8")
    return WhiteOpeningBook.load(book_path)


def test_local_api_flow_new_game_player_move_bot_move(tmp_path: Path) -> None:
    app = create_app()
    opening_book = make_book(tmp_path)
    fake_stockfish = FakeStockfishService(moves=["f1c4"])

    with TestClient(app) as client:
        app.state.opening_book = opening_book
        app.state.stockfish_service = fake_stockfish
        app.state.session_manager = GameSessionManager(
            opening_book=opening_book,
            stockfish_service=fake_stockfish,
        )

        new_game_response = client.post("/api/new-game", json={"bot_move_first": True})
        assert new_game_response.status_code == 200
        new_game_payload = new_game_response.json()
        assert new_game_payload["bot_color"] == "white"
        assert new_game_payload["bot_move"] == "e2e4"
        assert new_game_payload["source"] == "book"
        assert new_game_payload["book_probability_used"] == 1.0

        game_id = new_game_payload["game_id"]
        player_move_response = client.post(
            "/api/player-move",
            json={"game_id": game_id, "move": "e7e5"},
        )
        assert player_move_response.status_code == 200
        player_move_payload = player_move_response.json()
        assert player_move_payload["legal"] is True
        assert player_move_payload["applied_move_uci"] == "e7e5"

        bot_move_response = client.post("/api/bot-move", json={"game_id": game_id})
        assert bot_move_response.status_code == 200
        bot_move_payload = bot_move_response.json()
        assert bot_move_payload["chosen_move_uci"] == "g1f3"
        assert bot_move_payload["chosen_move_san"] == "Nf3"
        assert bot_move_payload["source"] == "book"
        assert bot_move_payload["book_probability_used"] == 0.9
