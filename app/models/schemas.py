from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(description="Health status string.")
    opening_book_loaded: bool = Field(description="Whether the opening book is loaded.")
    stockfish_ready: bool = Field(description="Whether Stockfish is configured and ready.")


class NewGameRequest(BaseModel):
    bot_move_first: bool = Field(
        default=False,
        description="If true, the White bot immediately makes the first move.",
    )


class NewGameResponse(BaseModel):
    game_id: str
    current_fen: str
    bot_color: str = "white"
    bot_move: str | None = None
    source: str | None = None
    book_probability_used: float | None = None


class PlayerMoveRequest(BaseModel):
    game_id: str
    move: str = Field(description="Player move in UCI format.")


class PlayerMoveResponse(BaseModel):
    game_id: str
    legal: bool
    applied_move_uci: str
    current_fen: str
    in_book: bool
    white_repertoire_decisions_made: int


class BotMoveRequest(BaseModel):
    game_id: str


class BotMoveResponse(BaseModel):
    game_id: str
    chosen_move_uci: str
    chosen_move_san: str
    resulting_fen: str
    source: str
    book_probability_used: float | None = None
    in_book_after_move: bool


class ResetGameRequest(BaseModel):
    game_id: str
    bot_move_first: bool = False


class ResetGameResponse(BaseModel):
    game_id: str
    current_fen: str
    bot_color: str = "white"
    bot_move: str | None = None
    source: str | None = None
    book_probability_used: float | None = None
