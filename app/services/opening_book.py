from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import chess
import chess.pgn

from app.services.pgn_parser import PGNParser


class OpeningBookGenerator:
    """Generate a White-only opening book from a master PGN repertoire file."""

    def __init__(self, parser: PGNParser | None = None, max_depth_ply: int = 24) -> None:
        self.parser = parser or PGNParser()
        self.max_depth_ply = max_depth_ply

    def build(self, source_path: Path, output_path: Path, max_depth_ply: int | None = None) -> dict:
        depth_limit = max_depth_ply if max_depth_ply is not None else self.max_depth_ply
        parsed = self.parser.parse_master_repertoire(source_path)
        positions: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

        if parsed.file_found:
            for parsed_game in parsed.games:
                self._traverse_node(
                    node=parsed_game.game,
                    positions=positions,
                    current_depth=0,
                    max_depth_ply=depth_limit,
                )

        serialized_positions = self._serialize_positions(positions)
        book = {
            "metadata": {
                "name": "White Repertoire Book",
                "max_depth_ply": depth_limit,
                "side": "white",
                "source_file": self._to_relative_source(source_path),
            },
            "positions": serialized_positions,
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(book, indent=2), encoding="utf-8")

        print(f"Master PGN found: {parsed.file_found}")
        print(f"Games processed: {parsed.games_processed}")
        print(f"White book positions created: {len(serialized_positions)}")

        return book

    def _traverse_node(
        self,
        node: chess.pgn.GameNode,
        positions: dict[str, dict[str, float]],
        current_depth: int,
        max_depth_ply: int,
    ) -> None:
        if current_depth >= max_depth_ply:
            return

        for child in node.variations:
            board = node.board()
            if board.turn == chess.WHITE and child.move is not None:
                fen = board.fen()
                positions[fen][child.move.uci()] += 1.0

            self._traverse_node(
                node=child,
                positions=positions,
                current_depth=current_depth + 1,
                max_depth_ply=max_depth_ply,
            )

    def _serialize_positions(self, positions: dict[str, dict[str, float]]) -> dict[str, dict[str, list[dict[str, float]]]]:
        serialized: dict[str, dict[str, list[dict[str, float]]]] = {}

        for fen in sorted(positions):
            moves = positions[fen]
            serialized[fen] = {
                "moves": [
                    {"uci": uci, "weight": weight}
                    for uci, weight in sorted(moves.items(), key=lambda item: (-item[1], item[0]))
                ]
            }

        return serialized

    def _to_relative_source(self, source_path: Path) -> str:
        try:
            return source_path.relative_to(Path.cwd()).as_posix()
        except ValueError:
            return source_path.name
