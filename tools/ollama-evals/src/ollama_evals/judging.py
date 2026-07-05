# <AI-Generated START>
"""Judge implementations for the LLM-as-judge scorer.

Two providers:
  * RubricJudge  -- default, fully offline. Prompts a (stronger) local Ollama model with
    a rubric and parses a JSON verdict. Zero extra dependencies.
  * DeepEvalJudge -- opt-in (`pip install '.[judge]'`). Wraps DeepEval's GEval metric,
    useful for richer metrics or a hosted judge model. The evaluator is injectable so the
    adapter is unit-testable without DeepEval installed.

Calibrate any judge against human labels before trusting it as a gate -- an uncalibrated
judge is worse than none. See the `calibrate` CLI command.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class Verdict:
    score: float  # normalised to 0.0-1.0
    reasoning: str = ""


_RUBRIC_PROMPT = """You are a strict evaluator. Score the RESPONSE against the CRITERIA \
on an integer scale from 1 (poor) to 5 (excellent).

CRITERIA: {criteria}

PROMPT:
{prompt}

RESPONSE:
{output}
{reference_block}
Reply with ONLY a JSON object of the form:
{{"score": <1-5>, "reasoning": "<one sentence>"}}"""

_JSON_OBJ = re.compile(r"\{.*\}", re.DOTALL)


class RubricJudge:
    """Judge backed by a local Ollama model prompted with a 1-5 rubric."""

    def __init__(self, client, model: str, temperature: float = 0.0, seed: int = 7) -> None:
        self._client = client
        self._model = model
        self._temperature = temperature
        self._seed = seed

    def score(self, *, criteria: str, prompt: str, output: str, reference=None) -> Verdict:
        reference_block = f"\nREFERENCE (a known-good answer):\n{reference}\n" if reference else ""
        content = _RUBRIC_PROMPT.format(
            criteria=criteria, prompt=prompt, output=output, reference_block=reference_block
        )
        result = self._client.chat(
            model=self._model,
            messages=[{"role": "user", "content": content}],
            temperature=self._temperature,
            seed=self._seed,
        )
        return _parse_verdict(result.content)

    def compare(self, *, criteria: str, prompt: str, output_a: str, output_b: str) -> str:
        """Side-by-side pairwise verdict: returns 'A', 'B', or 'tie'."""
        content = (
            f"Compare two responses on the CRITERIA and pick the better one.\n\n"
            f"CRITERIA: {criteria}\n\nPROMPT:\n{prompt}\n\n"
            f"RESPONSE A:\n{output_a}\n\nRESPONSE B:\n{output_b}\n\n"
            'Reply with ONLY JSON: {"winner": "A"|"B"|"tie"}'
        )
        result = self._client.chat(
            model=self._model,
            messages=[{"role": "user", "content": content}],
            temperature=self._temperature,
            seed=self._seed,
        )
        payload = _extract_json_obj(result.content) or {}
        winner = str(payload.get("winner", "tie")).upper()
        return winner if winner in ("A", "B") else "tie"


class DeepEvalJudge:
    """Judge backed by DeepEval's GEval metric. Evaluator is injectable for testing."""

    def __init__(self, model: str, evaluate_fn: Callable | None = None) -> None:
        self._model = model
        self._scorer = evaluate_fn or self._deepeval_scorer

    def score(self, *, criteria: str, prompt: str, output: str, reference=None) -> Verdict:
        raw_score, reason = self._scorer(prompt=prompt, output=output, criteria=criteria)
        return Verdict(float(raw_score), reason or "")

    def _deepeval_scorer(self, *, prompt, output, criteria):  # pragma: no cover - needs deepeval
        from deepeval.metrics import GEval
        from deepeval.test_case import LLMTestCase, LLMTestCaseParams

        metric = GEval(
            name="quality",
            criteria=criteria,
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            model=self._model,
        )
        case = LLMTestCase(input=prompt, actual_output=output)
        metric.measure(case)
        return float(metric.score), (metric.reason or "")


def build_judge(config, client):
    """Construct the judge selected by config.judge.provider."""
    jc = config.judge
    if jc.provider == "local":
        return RubricJudge(client, jc.model)
    if jc.provider == "remote":
        return DeepEvalJudge(jc.remote_model or jc.model)
    raise ValueError(f"unknown judge provider: {jc.provider!r}")


def _extract_json_obj(text: str):
    match = _JSON_OBJ.search(text)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _parse_verdict(text: str) -> Verdict:
    payload = _extract_json_obj(text)
    if payload is None or "score" not in payload:
        return Verdict(0.0, f"could not parse judge response: {text[:120]!r}")
    raw = max(1.0, min(5.0, float(payload["score"])))
    return Verdict((raw - 1.0) / 4.0, str(payload.get("reasoning", "")))
# <AI-Generated END>
