from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TextIO

import chess.pgn


@dataclass(slots=True)
class ParsedGame:
    """A parsed PGN game and any recoverable parser errors collected by python-chess."""

    index: int
    game: chess.pgn.Game
    errors: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ParsedPGNResult:
    """Parsed PGN stream metadata and successfully recovered games."""

    source_path: Path
    file_found: bool
    games: list[ParsedGame] = field(default_factory=list)
    skipped_sections: int = 0

    @property
    def games_processed(self) -> int:
        return len(self.games)


class PGNParser:
    """Stream a master PGN file using python-chess and preserve recoverable parse errors."""

    def parse_master_repertoire(self, pgn_path: Path) -> ParsedPGNResult:
        result = ParsedPGNResult(source_path=pgn_path, file_found=pgn_path.is_file())
        if not result.file_found:
            return result

        with pgn_path.open("r", encoding="utf-8", errors="replace") as handle:
            result.games = list(self.iter_games(handle))

        return result

    def iter_games(self, handle: TextIO) -> list[ParsedGame]:
        games: list[ParsedGame] = []
        game_index = 0

        while True:
            checkpoint = handle.tell()
            try:
                game = chess.pgn.read_game(handle)
            except Exception:
                # If parsing raises unexpectedly, move at least one line forward to
                # avoid looping forever on the same malformed chunk.
                if handle.tell() == checkpoint:
                    handle.readline()
                continue

            if game is None:
                break

            game_index += 1
            errors = [str(error) for error in getattr(game, "errors", [])]
            games.append(ParsedGame(index=game_index, game=game, errors=errors))

        return games
