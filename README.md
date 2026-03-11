# Harish Fish

Harish Fish is a local-first chess bot project scaffold built with FastAPI and Python 3.11. The intended system will parse a master White repertoire PGN with deeply nested variations, build a White-only opening book, and fall back to Stockfish once the bot leaves book.

This step sets up a clean, runnable project structure with:

- FastAPI backend entrypoint
- environment-based configuration
- placeholder service modules for the core chess logic
- simple frontend page for local backend testing
- data and script directories for repertoire input and generated artifacts

## Project Structure

```text
.
|-- app/
|   |-- api/
|   |   `-- routes.py
|   |-- core/
|   |   |-- config.py
|   |   `-- lifecycle.py
|   |-- models/
|   |   `-- schemas.py
|   |-- services/
|   |   |-- book_controller.py
|   |   |-- game_manager.py
|   |   |-- opening_book.py
|   |   |-- pgn_parser.py
|   |   `-- stockfish_service.py
|   |-- static/
|   |   |-- app.js
|   |   `-- styles.css
|   |-- templates/
|   |   `-- index.html
|   `-- main.py
|-- data/
|   |-- generated/
|   `-- repertoire_db/
|-- scripts/
|   `-- build_opening_book.py
|-- tests/
|   `-- test_health.py
|-- .env.example
`-- requirements.txt
```

## Requirements

- Python 3.11
- A local Stockfish binary later, when engine integration is implemented

## Quick Start

1. Create and activate a Python 3.11 virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy environment variables:

```bash
copy .env.example .env
```

4. Start the app:

```bash
uvicorn app.main:app --reload
```

5. Open the local test page:

```text
http://127.0.0.1:8000/
```

## Configuration

Settings are defined in [app/core/config.py](/C:/Users/Haris/OneDrive/Documents/GitHub/Random%20Projects/Harish-Fish/app/core/config.py) and loaded from `.env`.

Important values:

- `MASTER_PGN_PATH`: expected location of the master White repertoire PGN
- `GENERATED_BOOK_PATH`: output path for the generated opening book artifact
- `STOCKFISH_PATH`: path to the Stockfish binary
- `STOCKFISH_ELO`: target fallback engine strength

## Current Status

The project currently includes placeholders for:

- recursive PGN parsing
- White-only opening book generation
- book-following probability control
- Stockfish integration
- in-memory game/session management
- API routes for health, session start, and move submission

The only implemented logic so far is basic app bootstrapping, configuration loading, one health check, a simple static frontend, and a trivial probability helper stub in the book controller.

## Next Implementation Phase

- parse master PGN files including all nested variations
- build a traversable White-only opening book representation
- wire per-session book/out-of-book decisions
- integrate `python-chess` and Stockfish move selection
- add API request/response models and richer tests
