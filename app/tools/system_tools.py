from datetime import datetime

def get_current_time() -> str:
    """Return current system time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def add_numbers(a: int, b: int) -> int:
    """Add two integers."""
    return a + b
