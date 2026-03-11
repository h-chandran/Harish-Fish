from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.models.schemas import HealthResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check() -> HealthResponse:
    """Basic health endpoint for local development."""
    return HealthResponse(status="ok", detail="Service is running.")


@router.get("/", response_class=HTMLResponse, tags=["frontend"])
async def frontend_home(request: Request) -> HTMLResponse:
    """Render a lightweight test page for local interaction."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "Harish Fish Test Board"},
    )


@router.get("/api/book/status", tags=["book"])
async def book_status() -> dict[str, str]:
    """Placeholder route for future opening-book status reporting."""
    return {"message": "Opening book status endpoint placeholder."}


@router.post("/api/game/start", tags=["game"])
async def start_game() -> dict[str, str]:
    """Placeholder route for future game session bootstrapping."""
    return {"message": "Game start endpoint placeholder."}


@router.post("/api/game/move", tags=["game"])
async def submit_move() -> dict[str, str]:
    """Placeholder route for future move submission and engine response."""
    return {"message": "Move endpoint placeholder."}
