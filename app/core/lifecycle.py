from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown placeholder for service wiring."""
    app.state.services_ready = False

    # Future startup tasks:
    # - Validate configured paths.
    # - Load or generate the White opening book.
    # - Warm up the Stockfish engine wrapper.
    app.state.services_ready = True

    try:
        yield
    finally:
        # Future shutdown tasks:
        # - Flush in-memory sessions.
        # - Close engine subprocesses.
        app.state.services_ready = False
