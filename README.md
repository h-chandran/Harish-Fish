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

**Run all commands from the project root** (`Harish-Fish`), not from inside `venv`. Otherwise `requirements.txt` won’t be found and `uvicorn` won’t be available.

1. Create a virtual environment (once), then activate it from the project root:

   ```powershell
   cd "C:\Users\Haris\OneDrive\Documents\GitHub\Random Projects\Harish-Fish"
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install dependencies (with your shell **in the project root**):

   ```powershell
   pip install -r requirements.txt
   ```

3. Copy environment variables:

   ```powershell
   copy .env.example .env
   ```
   Then set `STOCKFISH_PATH` in `.env` if needed (e.g. `stockfish/stockfish-windows-x86-64-avx2.exe`).

4. Start the app (still from the project root):

   ```powershell
   uvicorn app.main:app --reload
   ```

   **Or** use the helper script (activates venv, installs deps, then starts the app):

   ```powershell
   .\run.ps1
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
- FastAPI session API for local testing
- simple browser frontend for local end-to-end testing
- test coverage for book generation, book control, bot move routing, and API flow

## Next Implementation Phase

- add persistent or managed session state
- calibrate Stockfish fallback strength against your target style
- add richer API request/response models
- optionally add drag-and-drop board interaction or richer move highlighting

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

## Browser Testing

The local frontend is served from the same FastAPI app at the root URL:

```text
http://127.0.0.1:8000/
```

Basic browser flow:

1. Start the backend with Uvicorn.
2. Open the root URL in your browser.
3. Click `Create New Game`.
4. Leave `Bot makes White's first move automatically` checked if you want the normal White-bot flow.
5. Enter Black moves in UCI format such as `e7e5`, or click a source square and destination square on the board to fill the move box.
6. Click `Play Black Move`.
7. Click `Request Bot White Move`.
8. Repeat to continue testing multiple plies.

The page shows:

- current board
- move list
- latest bot move
- whether the bot move came from `book` or `stockfish`
- book probability used
- current FEN

Important local note:

- If your generated opening book is empty and `STOCKFISH_PATH` is not configured, the bot will not be able to produce a White move outside the book.
