from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.models.schemas import (
    BotMoveRequest,
    BotMoveResponse,
    HealthResponse,
    NewGameRequest,
    NewGameResponse,
    PlayerMoveRequest,
    PlayerMoveResponse,
    ResetGameRequest,
    ResetGameResponse,
)
from app.services.game_manager import InvalidMoveError, SessionNotFoundError
from app.services.stockfish_service import StockfishConfigurationError

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check(request: Request) -> HealthResponse:
    """Basic health endpoint for local development."""
    opening_book = getattr(request.app.state, "opening_book", None)
    stockfish_service = getattr(request.app.state, "stockfish_service", None)
    return HealthResponse(
        status="ok",
        opening_book_loaded=opening_book is not None,
        stockfish_ready=bool(stockfish_service and stockfish_service.is_ready),
    )


@router.get("/", response_class=HTMLResponse, tags=["frontend"])
async def frontend_home(request: Request) -> HTMLResponse:
    """Render a lightweight test page for local interaction."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "Harish Fish Test Board"},
    )


@router.post("/api/new-game", response_model=NewGameResponse, tags=["game"])
async def new_game(request: Request, payload: NewGameRequest) -> NewGameResponse:
    session_manager = _get_session_manager(request)
    session, bot_result = session_manager.create_session(bot_move_first=payload.bot_move_first)
    return NewGameResponse(
        game_id=session.game_id,
        current_fen=session.board.fen(),
        bot_move=bot_result.move.uci() if bot_result else None,
        source=bot_result.source if bot_result else None,
        book_probability_used=_book_probability(bot_result),
    )


@router.post("/api/player-move", response_model=PlayerMoveResponse, tags=["game"])
async def player_move(request: Request, payload: PlayerMoveRequest) -> PlayerMoveResponse:
    session_manager = _get_session_manager(request)
    try:
        session = session_manager.apply_player_move(payload.game_id, payload.move)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidMoveError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PlayerMoveResponse(
        game_id=session.game_id,
        legal=True,
        applied_move_uci=payload.move,
        current_fen=session.board.fen(),
        in_book=session.in_book,
        white_repertoire_decisions_made=session.white_repertoire_decisions_made,
    )


@router.post("/api/bot-move", response_model=BotMoveResponse, tags=["game"])
async def bot_move(request: Request, payload: BotMoveRequest) -> BotMoveResponse:
    session_manager = _get_session_manager(request)
    try:
        session_before = session_manager.get_session(payload.game_id)
        board_before_move = session_before.board.copy()
        result = session_manager.make_bot_move(payload.game_id)
        session_after = session_manager.get_session(payload.game_id)
        san = board_before_move.san(result.move)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidMoveError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except StockfishConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return BotMoveResponse(
        game_id=payload.game_id,
        chosen_move_uci=result.move.uci(),
        chosen_move_san=san,
        resulting_fen=session_after.board.fen(),
        source=result.source,
        book_probability_used=_book_probability(result),
        in_book_after_move=session_after.in_book,
    )


@router.post("/api/reset-game", response_model=ResetGameResponse, tags=["game"])
async def reset_game(request: Request, payload: ResetGameRequest) -> ResetGameResponse:
    session_manager = _get_session_manager(request)
    try:
        session, bot_result = session_manager.reset_session(
            payload.game_id,
            bot_move_first=payload.bot_move_first,
        )
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except StockfishConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ResetGameResponse(
        game_id=session.game_id,
        current_fen=session.board.fen(),
        bot_move=bot_result.move.uci() if bot_result else None,
        source=bot_result.source if bot_result else None,
        book_probability_used=_book_probability(bot_result),
    )


def _get_session_manager(request: Request):
    session_manager = getattr(request.app.state, "session_manager", None)
    if session_manager is None:
        raise HTTPException(status_code=503, detail="Session manager is not available.")
    return session_manager


def _book_probability(result) -> float | None:
    if result is None or result.book_decision is None:
        return None
    return result.book_decision.probability_used
