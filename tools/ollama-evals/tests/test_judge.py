import pytest

from ollama_evals.config import Config, JudgeConfig
from ollama_evals.judging import DeepEvalJudge, RubricJudge, Verdict, build_judge
from ollama_evals.scorers import score_output


class FakeJudge:
    def __init__(self, score, reasoning="because"):
        self._verdict = Verdict(score, reasoning)

    def score(self, *, criteria, prompt, output, reference=None):
        return self._verdict


def test_llm_judge_passes_above_threshold():
    ctx = {"judge": FakeJudge(0.9), "prompt": "explain X"}
    spec = {"type": "judge", "criteria": "clarity", "threshold": 0.7}
    r = score_output("a good answer", spec, ctx)
    assert r.passed and r.score == 0.9


def test_llm_judge_fails_below_threshold():
    ctx = {"judge": FakeJudge(0.4), "prompt": "explain X"}
    spec = {"type": "judge", "criteria": "clarity", "threshold": 0.7}
    r = score_output("meh", spec, ctx)
    assert not r.passed and r.score == 0.4


def test_llm_judge_without_judge_raises():
    with pytest.raises(RuntimeError):
        score_output("x", {"type": "judge", "criteria": "clarity"}, {})


class FakeChatResult:
    def __init__(self, content):
        self.content = content


class FakeClient:
    def __init__(self, content):
        self._content = content
        self.last_call = None

    def chat(self, **kwargs):
        self.last_call = kwargs
        return FakeChatResult(self._content)


def test_rubric_judge_parses_and_normalizes_1_to_5():
    client = FakeClient('{"score": 5, "reasoning": "excellent"}')
    judge = RubricJudge(client, model="judge-model")
    v = judge.score(criteria="clarity", prompt="explain X", output="answer")
    assert v.score == 1.0  # 5 -> 1.0
    assert "excellent" in v.reasoning
    assert client.last_call["model"] == "judge-model"


def test_rubric_judge_midpoint():
    judge = RubricJudge(FakeClient('{"score": 3, "reasoning": "ok"}'), model="j")
    assert judge.score(criteria="c", prompt="p", output="o").score == 0.5


def test_rubric_judge_handles_unparseable_response():
    judge = RubricJudge(FakeClient("I think it's pretty good honestly"), model="j")
    v = judge.score(criteria="c", prompt="p", output="o")
    assert v.score == 0.0
    assert "parse" in v.reasoning.lower()


def test_build_judge_local_returns_rubric_judge():
    cfg = Config(judge=JudgeConfig(provider="local", model="qwen2.5:14b"))
    assert isinstance(build_judge(cfg, client=FakeClient("{}")), RubricJudge)


def test_build_judge_remote_returns_deepeval_judge():
    cfg = Config(judge=JudgeConfig(provider="remote", remote_model="claude"))
    assert isinstance(build_judge(cfg, client=FakeClient("{}")), DeepEvalJudge)


def test_deepeval_judge_uses_injected_evaluator():
    def stub_scorer(*, prompt, output, criteria):
        return 0.8, "solid"

    judge = DeepEvalJudge(model="claude", evaluate_fn=stub_scorer)
    v = judge.score(criteria="clarity", prompt="p", output="o")
    assert v.score == 0.8 and v.reasoning == "solid"


def test_rubric_judge_pairwise_compare():
    judge = RubricJudge(FakeClient('{"winner": "B"}'), model="j")
    assert judge.compare(criteria="c", prompt="p", output_a="a", output_b="b") == "B"


def test_rubric_judge_pairwise_defaults_to_tie_on_junk():
    judge = RubricJudge(FakeClient("no json here"), model="j")
    assert judge.compare(criteria="c", prompt="p", output_a="a", output_b="b") == "tie"


def test_build_judge_unknown_provider_raises():
    cfg = Config(judge=JudgeConfig(provider="nope"))
    with pytest.raises(ValueError):
        build_judge(cfg, client=FakeClient("{}"))


# --- Commit B: a parse failure must be distinguishable from a genuine zero -----------


class SequenceClient:
    """Returns each scripted content in turn; records how many calls were made."""

    def __init__(self, contents):
        self._contents = list(contents)
        self.n_calls = 0

    def chat(self, **kwargs):
        self.n_calls += 1
        idx = min(self.n_calls - 1, len(self._contents) - 1)
        return FakeChatResult(self._contents[idx])


def test_verdict_defaults_to_parsed():
    assert Verdict(0.5).parsed is True


def test_unparseable_verdict_is_flagged_not_silently_zero():
    judge = RubricJudge(FakeClient("no json at all"), model="j", retries=0)
    v = judge.score(criteria="c", prompt="p", output="o")
    assert v.score == 0.0
    assert v.parsed is False


def test_a_genuine_low_score_is_still_marked_parsed():
    judge = RubricJudge(FakeClient('{"score": 1, "reasoning": "bad"}'), model="j")
    v = judge.score(criteria="c", prompt="p", output="o")
    assert v.score == 0.0  # 1/5 normalises to 0.0 — same number, different meaning
    assert v.parsed is True


def test_rubric_judge_retries_once_on_parse_failure():
    client = SequenceClient(["garbage", '{"score": 4, "reasoning": "fine"}'])
    judge = RubricJudge(client, model="j", retries=1)
    v = judge.score(criteria="c", prompt="p", output="o")
    assert client.n_calls == 2
    assert v.parsed is True
    assert v.score == 0.75


def test_rubric_judge_does_not_retry_when_first_response_parses():
    client = SequenceClient(['{"score": 5, "reasoning": "great"}', "garbage"])
    judge = RubricJudge(client, model="j", retries=1)
    v = judge.score(criteria="c", prompt="p", output="o")
    assert client.n_calls == 1
    assert v.score == 1.0


def test_llm_judge_scorer_marks_parse_failure_in_metadata():
    class UnparseableJudge:
        def score(self, *, criteria, prompt, output, reference=None):
            return Verdict(0.0, "could not parse", parsed=False)

    r = score_output("x", {"type": "judge", "criteria": "c"}, {"judge": UnparseableJudge()})
    assert r.metadata["parse_failure"] is True


def test_llm_judge_scorer_has_no_parse_failure_flag_on_success():
    r = score_output("x", {"type": "judge", "criteria": "c"}, {"judge": FakeJudge(0.9)})
    assert r.metadata.get("parse_failure", False) is False
