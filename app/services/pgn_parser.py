from pathlib import Path


class PGNParser:
    """Placeholder for recursive PGN parsing across nested variations."""

    def parse_master_repertoire(self, pgn_path: Path) -> dict:
        """
        Parse a master PGN file into an intermediate structure.

        Future implementation should:
        - ignore comments, prose, and annotations
        - recurse through all side variations
        - preserve traversal through Black moves so White continuations remain reachable
        """
        raise NotImplementedError("PGN parsing is not implemented yet.")
