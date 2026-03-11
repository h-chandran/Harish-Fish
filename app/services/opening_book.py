from pathlib import Path


class OpeningBookGenerator:
    """Placeholder for generating a White-only opening book artifact."""

    def build(self, source_path: Path, output_path: Path) -> dict:
        """
        Generate the serialized White-only opening book.

        Future implementation should store only White repertoire moves while
        traversing Black replies as connectors in the move tree.
        """
        raise NotImplementedError("Opening book generation is not implemented yet.")
