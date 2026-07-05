"""Pluggable scorers: deterministic, code-execution, LLM-as-judge, tool-use.

Importing this package registers the built-in scorers via their modules' side effects.
"""

from . import (
    code_exec,  # noqa: F401  (import registers code_exec)
    deterministic,  # noqa: F401  (import registers exact/contains/regex/json_schema)
)
from . import judge as _judge  # noqa: F401  (import registers judge)
from . import tool_use as _tool_use  # noqa: F401  (import registers tool_use)
from .base import ScoreResult, get_scorer, register, score_output

__all__ = ["ScoreResult", "get_scorer", "register", "score_output"]
