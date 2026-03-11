class GameSessionManager:
    """Placeholder in-memory manager for local test sessions."""

    def create_session(self) -> dict:
        """Create a new game session placeholder."""
        raise NotImplementedError("Game/session management is not implemented yet.")

    def apply_player_move(self, session_id: str, move_uci: str) -> dict:
        """Apply a player move and compute the bot response placeholder."""
        raise NotImplementedError("Move handling is not implemented yet.")
