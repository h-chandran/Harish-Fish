import random


class BookController:
    """Placeholder for book-following probability and out-of-book transitions."""

    def should_follow_book(self, white_decision_index: int) -> bool:
        """
        Decide whether to stay in book using the requested decaying probability.

        Future behavior:
        - first White repertoire decision: 100%
        - each later White decision: minus 10 percentage points
        - once false, the game remains permanently out of book
        """
        threshold = max(0, 100 - max(0, white_decision_index - 1) * 10)
        return random.randint(1, 100) <= threshold
