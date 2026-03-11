from app.core.config import get_settings


def main() -> None:
    """Placeholder CLI entrypoint for future opening-book generation."""
    settings = get_settings()
    print(
        "Opening book generation is not implemented yet.\n"
        f"Master PGN path: {settings.master_pgn_path}\n"
        f"Generated book path: {settings.generated_book_path}"
    )


if __name__ == "__main__":
    main()
