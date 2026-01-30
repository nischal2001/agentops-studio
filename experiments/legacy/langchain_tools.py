"""
LEGACY CODE
Kept for learning/reference.
Not used in Patient Journey Orchestration Agent.
"""









# from langchain.tools import Tool
# from app.tools.system_tools import get_current_time, add_numbers

# tools = [
#     Tool(
#         name="get_current_time",
#         func=get_current_time,
#         description="Get the current system time"
#     ),
#     Tool(
#         name="add_numbers",
#         func=add_numbers,
#         description="Add two numbers together"
#     )
# ]


from langchain_core.tools import tool
from experiments.legacy.system_tools import get_current_time, add_numbers


@tool
def current_time() -> str:
    """Get the current system time."""
    return get_current_time()


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return add_numbers(a, b)


tools = [current_time, add]
