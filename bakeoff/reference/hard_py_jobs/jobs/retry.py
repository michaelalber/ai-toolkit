"""Retry delays."""


def backoff(attempt, base=1.0, cap=30.0):
    """Delay before retry number `attempt` (1-based)."""
    if attempt < 1:
        raise ValueError("attempt is 1-based")
    return min(cap, base * 2 ** (attempt - 1))
