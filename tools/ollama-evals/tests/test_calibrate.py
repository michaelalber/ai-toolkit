from ollama_evals.calibrate import CalibrationExample, calibrate
from ollama_evals.judging import Verdict


class LookupJudge:
    """Returns a score computed from the output text, for deterministic tests."""

    def __init__(self, score_fn):
        self._score_fn = score_fn

    def score(self, *, criteria, prompt, output, reference=None):
        return Verdict(self._score_fn(output), "")


def _examples():
    return [
        CalibrationExample("g1", "p", "great answer", "c", human_score=1.0),
        CalibrationExample("g2", "p", "great answer 2", "c", human_score=1.0),
        CalibrationExample("b1", "p", "bad", "c", human_score=0.0),
        CalibrationExample("b2", "p", "bad 2", "c", human_score=0.0),
    ]


def test_perfect_agreement():
    judge = LookupJudge(lambda o: 1.0 if o.startswith("great") else 0.0)
    result = calibrate(judge, _examples())
    assert result.n == 4
    assert result.agreement == 1.0


def test_partial_agreement():
    # Judge always says "pass" -> agrees with the 2 human-good, disagrees with the 2 bad.
    judge = LookupJudge(lambda o: 1.0)
    result = calibrate(judge, _examples())
    assert result.agreement == 0.5


def test_rows_capture_scores():
    judge = LookupJudge(lambda o: 0.9)
    result = calibrate(judge, _examples())
    assert len(result.rows) == 4
    assert all("judge_score" in row for row in result.rows)
