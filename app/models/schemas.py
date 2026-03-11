from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(description="Health status string.")
    detail: str = Field(description="Short status detail.")


class GameSessionState(BaseModel):
    """Placeholder session state shape for future game management."""

    session_id: str
    fen: str
    in_book: bool = True
    white_book_decision_index: int = 0
