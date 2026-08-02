# <AI-Generated START>
"""Scorers skill-evals registers into the ollama-evals scorer registry.

Imported for their registration side effects, exactly as ollama-evals does for its own.
Registration is lazy: importing this package without ollama-evals installed must not
raise, because the L1 lint has to keep working with no LLM stack at all.
"""

from __future__ import annotations

from .._ollama import available

if available():  # pragma: no branch - trivial guard
    from . import route_choice, skill_rubric  # noqa: F401
# <AI-Generated END>
