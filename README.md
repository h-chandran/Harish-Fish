# Harish Fish

Harish Fish is a local-first chess bot project scaffold built with FastAPI and Python 3.11. The intended system parses a master White repertoire PGN with deeply nested variations, builds a White-only opening book, and falls back to Stockfish once the bot leaves book.

The project now includes:

- FastAPI backend entrypoint
- environment-based configuration
- recursive opening-book generation from a master PGN
- runtime White-only book controller with decaying usage probability
- Stockfish fallback integration through `python-chess`
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
- A local Stockfish binary for fallback play outside the repertoire book

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
- `STOCKFISH_THREADS`: fallback engine thread count
- `STOCKFISH_HASH_MB`: fallback engine hash size in MB
- `STOCKFISH_MOVE_TIME_MS`: fallback move time budget in milliseconds
- `STOCKFISH_LIMIT_STRENGTH`: whether to use Stockfish's Elo limiting mode
- `STOCKFISH_ELO`: target fallback engine strength
- `STOCKFISH_SKILL_LEVEL`: optional extra tuning knob if you want to override the default

Default fallback tuning is chosen to aim for approximately 2400 strength:

- `STOCKFISH_THREADS=1`
- `STOCKFISH_HASH_MB=128`
- `STOCKFISH_MOVE_TIME_MS=500`
- `STOCKFISH_LIMIT_STRENGTH=true`
- `STOCKFISH_ELO=2400`

This strength target is approximate. Real playing strength will vary by Stockfish version, hardware, and move time, so calibration can be tightened later if needed.

## Current Status

Implemented so far:

- recursive PGN parsing using `python-chess`
- White-only opening book generation with weighted move accumulation
- runtime White book controller with permanent out-of-book state
- Stockfish fallback service with startup and shutdown support
- bot move arbitration between book and Stockfish
- simple frontend health/test page
- test coverage for book generation, book control, and bot move routing

## Next Implementation Phase

- connect the bot move service to API/game-session routes
- add persistent or managed session state
- improve frontend board interaction for local testing
- calibrate Stockfish fallback strength against your target style
- add richer API request/response models

## Demo Commands

Regenerate the opening book:

```bash
python scripts\build_opening_book.py
```

Show a single controller decision from the starting position:

```bash
python scripts\demo_book_controller.py
```

Play Black against the bot in the terminal:

```bash
python scripts\demo_play_vs_bot.py
```
