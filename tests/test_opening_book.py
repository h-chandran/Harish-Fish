import json
from pathlib import Path

import chess

from app.services.opening_book import OpeningBookGenerator
from app.services.pgn_parser import PGNParser


def build_book_from_pgn(tmp_path: Path, pgn_text: str, max_depth_ply: int = 24) -> dict:
    source_path = tmp_path / "master_repertoire.pgn"
    output_path = tmp_path / "white_opening_book.json"
    source_path.write_text(pgn_text, encoding="utf-8")

    generator = OpeningBookGenerator(max_depth_ply=max_depth_ply)
    return generator.build(source_path=source_path, output_path=output_path)


def test_recursive_variation_traversal_reaches_later_white_positions(tmp_path: Path) -> None:
    book = build_book_from_pgn(
        tmp_path,
        """
[Event "Variation Test"]

1. e4 (1. d4 d5 2. c4) 1... e5 (1... c5 2. Nf3) 2. Nf3 (2. Bc4)
""".strip(),
    )

    start_fen = chess.Board().fen()
    e4_c5_board = chess.Board()
    e4_c5_board.push_uci("e2e4")
    e4_c5_board.push_uci("c7c5")
    e4_e5_board = chess.Board()
    e4_e5_board.push_uci("e2e4")
    e4_e5_board.push_uci("e7e5")
    d4_d5_board = chess.Board()
    d4_d5_board.push_uci("d2d4")
    d4_d5_board.push_uci("d7d5")

    assert {move["uci"] for move in book["positions"][start_fen]["moves"]} == {"e2e4", "d2d4"}
    assert {move["uci"] for move in book["positions"][e4_c5_board.fen()]["moves"]} == {"g1f3"}
    assert {move["uci"] for move in book["positions"][e4_e5_board.fen()]["moves"]} == {"f1c4", "g1f3"}
    assert {move["uci"] for move in book["positions"][d4_d5_board.fen()]["moves"]} == {"c2c4"}


def test_white_only_move_recording(tmp_path: Path) -> None:
    book = build_book_from_pgn(
        tmp_path,
        """
[Event "White Only"]

1. e4 e5 2. Nf3 Nc6 3. Bb5
""".strip(),
    )

    for fen, entry in book["positions"].items():
        assert chess.Board(fen).turn == chess.WHITE
        assert all(chess.Board(fen).turn == chess.WHITE for _ in entry["moves"])

    e4_board = chess.Board()
    e4_board.push_uci("e2e4")
    assert e4_board.fen() not in book["positions"]


def test_duplicate_move_weight_accumulation(tmp_path: Path) -> None:
    book = build_book_from_pgn(
        tmp_path,
        """
[Event "Game 1"]

1. e4 e5 2. Nf3

[Event "Game 2"]

1. e4 c5 2. Nf3
""".strip(),
    )

    start_fen = chess.Board().fen()
    moves = {move["uci"]: move["weight"] for move in book["positions"][start_fen]["moves"]}

    assert moves["e2e4"] == 2.0


def test_comments_annotations_and_nags_are_ignored(tmp_path: Path) -> None:
    book = build_book_from_pgn(
        tmp_path,
        """
[Event "Annotated"]

1. e4! {King's pawn opening prose that should be ignored.} e5?! 2. Nf3
(2. Bc4!? {Bishop development comment}) 2... Nc6
""".strip(),
    )

    start_fen = chess.Board().fen()
    e4_e5_board = chess.Board()
    e4_e5_board.push_uci("e2e4")
    e4_e5_board.push_uci("e7e5")
    moves_from_start = {move["uci"] for move in book["positions"][start_fen]["moves"]}
    moves_after_e4_e5 = {move["uci"] for move in book["positions"][e4_e5_board.fen()]["moves"]}

    assert moves_from_start == {"e2e4"}
    assert moves_after_e4_e5 == {"f1c4", "g1f3"}


def test_malformed_pgn_sections_do_not_block_other_games(tmp_path: Path) -> None:
    source_path = tmp_path / "master_repertoire.pgn"
    output_path = tmp_path / "white_opening_book.json"
    source_path.write_text(
        """
[Event "Bad"]

1. e4 e5 nonsense 2. Nf3 Nc6

[Event "Good"]

1. d4 d5 2. c4
""".strip(),
        encoding="utf-8",
    )

    parser = PGNParser()
    parsed = parser.parse_master_repertoire(source_path)
    generator = OpeningBookGenerator(parser=parser)
    book = generator.build(source_path=source_path, output_path=output_path)

    assert parsed.file_found is True
    assert parsed.games_processed == 2

    start_fen = chess.Board().fen()
    moves = {move["uci"] for move in book["positions"][start_fen]["moves"]}

    assert moves == {"d2d4", "e2e4"}
    assert json.loads(output_path.read_text(encoding="utf-8"))["metadata"]["source_file"] == "master_repertoire.pgn"
