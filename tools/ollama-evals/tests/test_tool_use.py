from ollama_evals.scorers import score_output


def _ctx(tool_calls):
    return {"tool_calls": tool_calls}


def test_exact_tool_and_args_pass():
    spec = {"type": "tool_use", "expected": {"name": "get_weather", "arguments": {"city": "Paris"}}}
    ctx = _ctx([{"name": "get_weather", "arguments": {"city": "Paris"}}])
    r = score_output("", spec, ctx)
    assert r.passed and r.score == 1.0


def test_right_tool_wrong_args_partial_credit_no_pass():
    spec = {"type": "tool_use", "expected": {"name": "get_weather", "arguments": {"city": "Paris"}}}
    ctx = _ctx([{"name": "get_weather", "arguments": {"city": "London"}}])
    r = score_output("", spec, ctx)
    assert not r.passed
    assert 0.0 < r.score < 1.0  # got the tool name, missed the argument


def test_wrong_tool_scores_zero():
    spec = {"type": "tool_use", "expected": {"name": "get_weather", "arguments": {"city": "Paris"}}}
    ctx = _ctx([{"name": "send_email", "arguments": {}}])
    r = score_output("", spec, ctx)
    assert not r.passed and r.score == 0.0


def test_no_tool_call_scores_zero():
    spec = {"type": "tool_use", "expected": {"name": "get_weather"}}
    r = score_output("", spec, _ctx([]))
    assert not r.passed and r.score == 0.0


def test_non_dict_arguments_do_not_pass():
    spec = {"type": "tool_use", "expected": {"name": "get_weather", "arguments": {"city": "Paris"}}}
    ctx = _ctx([{"name": "get_weather", "arguments": "Paris"}])  # model emitted a bare string
    r = score_output("", spec, ctx)
    assert not r.passed
    assert "not valid JSON object" in r.detail


def test_name_only_expectation_passes_when_tool_selected():
    spec = {"type": "tool_use", "expected": {"name": "get_weather"}}
    ctx = _ctx([{"name": "get_weather", "arguments": {"city": "Paris"}}])
    r = score_output("", spec, ctx)
    assert r.passed and r.score == 1.0
