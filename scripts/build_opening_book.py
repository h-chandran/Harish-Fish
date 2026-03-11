from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import get_settings
from app.services.opening_book import OpeningBookGenerator


def main() -> None:
    """Build the White opening book from the configured master PGN."""
    settings = get_settings()
    generator = OpeningBookGenerator(max_depth_ply=settings.book_max_depth_ply)

    source_path = Path(settings.master_pgn_path)
    output_path = Path(settings.generated_book_path)
    generator.build(
        source_path=source_path,
        output_path=output_path,
        max_depth_ply=settings.book_max_depth_ply,
    )


if __name__ == "__main__":
    main()
