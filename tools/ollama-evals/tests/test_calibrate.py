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


def test_pass_mark_matches_the_judge_scorer():
    """A 3/5 verdict (0.5) fails a real chat case (threshold 0.7), so it must not count
    as agreeing with a human 'good' label here."""
    result = calibrate(LookupJudge(lambda o: 0.5), _examples()[:1])
    assert result.agreement == 0.0


def test_false_passes_and_false_fails_are_counted_separately():
    scores = {"great answer": 0.0, "great answer 2": 0.75, "bad": 1.0, "bad 2": 0.25}
    judge = LookupJudge(scores.__getitem__)
    result = calibrate(judge, _examples())
    assert result.false_passes == ["b1"]  # judge passed an answer a human failed
    assert result.false_fails == ["g1"]   # judge failed an answer a human passed


class UnreadableJudge:
    def score(self, *, criteria, prompt, output, reference=None):
        return Verdict(0.0, "could not parse", parsed=False)


def test_an_unreadable_verdict_never_counts_as_agreement():
    result = calibrate(UnreadableJudge(), _examples())
    assert result.agreement == 0.0  # not 0.5 from "agreeing" with the two bad examples
    assert result.unparsed == ["g1", "g2", "b1", "b2"]
