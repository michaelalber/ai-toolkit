# <AI-Generated START>
import io
import json

import harness
import pytest
from harness import HERE, NUM_CTX, auth_headers, build_options, load_task_config, restore_tests


def test_default_options_force_context_and_zero_temperature():
    assert build_options(modelfile_defaults=False) == {"num_ctx": NUM_CTX, "temperature": 0}


def test_modelfile_defaults_sends_no_overrides():
    assert build_options(modelfile_defaults=True) == {}


def _dirs(tmp_path):
    src, work = tmp_path / "src", tmp_path / "work"
    src.mkdir()
    work.mkdir()
    return src, work


def test_clean_run_is_not_tampered(tmp_path):
    src, work = _dirs(tmp_path)
    (src / "test_a.py").write_text("orig")
    (work / "test_a.py").write_text("orig")
    assert restore_tests(src, work) is False


def test_edited_test_is_detected_and_reverted(tmp_path):
    src, work = _dirs(tmp_path)
    (src / "test_a.py").write_text("orig")
    (work / "test_a.py").write_text("hacked")
    assert restore_tests(src, work) is True
    assert (work / "test_a.py").read_text() == "orig"


def test_deleted_nested_test_is_restored(tmp_path):
    src, work = _dirs(tmp_path)
    (src / "pkg").mkdir()
    (src / "pkg" / "test_b.py").write_text("orig")
    assert restore_tests(src, work) is True
    assert (work / "pkg" / "test_b.py").read_text() == "orig"


def test_custom_globs_protect_csharp_tests(tmp_path):
    src, work = _dirs(tmp_path)
    (src / "CartTests.cs").write_text("orig")
    (work / "CartTests.cs").write_text("hacked")
    assert restore_tests(src, work, ["*Tests.cs"]) is True
    assert (work / "CartTests.cs").read_text() == "orig"


@pytest.mark.parametrize("name", ["conftest.py", "pkg/conftest.py", "pytest.ini", "pyproject.toml",
                                  "sitecustomize.py", "Directory.Build.props"])
def test_model_added_grader_config_is_removed_and_flagged(tmp_path, name):
    src, work = _dirs(tmp_path)
    (work / name).parent.mkdir(parents=True, exist_ok=True)
    (work / name).write_text("hijack")
    assert restore_tests(src, work) is True
    assert not (work / name).exists()


def test_task_shipped_grader_config_is_restored(tmp_path):
    src, work = _dirs(tmp_path)
    (src / "pyproject.toml").write_text("orig")
    (work / "pyproject.toml").write_text("hacked")
    assert restore_tests(src, work) is True
    assert (work / "pyproject.toml").read_text() == "orig"


def test_conftest_cannot_force_a_stub_to_pass(tmp_path):
    from sandbox import Sandbox
    src = HERE / "tasks" / "hard_spec"
    import shutil
    shutil.copytree(src, tmp_path, dirs_exist_ok=True)
    (tmp_path / "conftest.py").write_text(
        "import pytest\n@pytest.hookimpl(hookwrapper=True)\n"
        "def pytest_runtest_makereport(item, call):\n    (yield).get_result().outcome = 'passed'\n")
    assert restore_tests(src, tmp_path) is True
    assert Sandbox(tmp_path).run_tests()[0] is False


def test_task_without_hidden_tests_has_none(tmp_path, monkeypatch):
    monkeypatch.setattr(harness, "HERE", tmp_path)
    assert harness.load_hidden("anything") == {}


def test_load_hidden_reads_nested_files_relative_to_the_task(tmp_path, monkeypatch):
    monkeypatch.setattr(harness, "HERE", tmp_path)
    (tmp_path / "hidden" / "t" / "pkg").mkdir(parents=True)
    (tmp_path / "hidden" / "t" / "pkg" / "test_h.py").write_text("x")
    assert harness.load_hidden("t") == {harness.Path("pkg/test_h.py"): b"x"}


def test_hidden_grade_is_none_without_hidden_tests(tmp_path):
    from sandbox import Sandbox
    assert harness.hidden_passed(Sandbox(tmp_path), {}) is None


@pytest.mark.parametrize("body,expected", [("def test_ok():\n    pass\n", True),
                                           ("def test_bad():\n    assert False\n", False)])
def test_hidden_grade_runs_the_hidden_tests_in_the_workdir(tmp_path, body, expected):
    from sandbox import Sandbox
    assert harness.hidden_passed(Sandbox(tmp_path), {harness.Path("test_hidden.py"): body.encode()}) is expected


def test_summary_shows_hidden_result_and_blank_when_absent():
    base = {"model": "m", "task": "t", "passed": True, "turns": 1, "tool_errors": 0, "tool_calls": 1,
            "gen_tok_s": 1, "wall_s": 1, "mem_gb": 1, "tests_tampered": False, "error": None}
    table = harness.summarize([{**base, "hidden_passed": False}, {**base, "hidden_passed": None}])
    assert "| PASS | FAIL |" in table.splitlines()[2]
    assert "| PASS |  |" in table.splitlines()[3]


def _row(model, task, passed, hidden, wall=10):
    return {"model": model, "task": task, "passed": passed, "hidden_passed": hidden, "wall_s": wall}


def test_aggregate_counts_passes_per_model_and_task_with_a_model_total():
    rows = [_row("m1", "t1", True, True), _row("m1", "t1", True, False), _row("m1", "t1", False, False),
            _row("m1", "t2", True, None, 30), _row("m1", "t2", True, None, 20)]
    lines = harness.aggregate(rows).splitlines()
    assert lines[2] == "| m1 | t1 | 2/3 | 1/3 | 10.0 |"
    assert lines[3] == "| m1 | t2 | 2/2 |  | 25.0 |"
    assert lines[4] == "| **m1** | **all** | **4/5** | **1/3** |  |"


def test_aggregate_keeps_models_in_first_seen_order():
    rows = [_row("zeta", "t", True, True), _row("alpha", "t", False, False)]
    body = harness.aggregate(rows)
    assert body.index("zeta") < body.index("alpha")


def test_task_without_config_defaults_to_pytest(tmp_path):
    cfg = load_task_config(tmp_path)
    assert cfg["test_globs"] == ["test_*.py"]
    assert "pytest" in cfg["test_cmd"]
    assert cfg["test_timeout"] == 60


def test_task_json_overrides_defaults(tmp_path):
    (tmp_path / "task.json").write_text(json.dumps(
        {"test_cmd": ["dotnet", "test"], "test_globs": ["*Tests.cs"], "test_timeout": 180}))
    assert load_task_config(tmp_path) == {"test_cmd": ["dotnet", "test"], "test_globs": ["*Tests.cs"],
                                          "test_timeout": 180}


def test_no_env_var_means_no_auth_header():
    assert auth_headers(None) == {}


def test_auth_header_is_bearer_from_env(monkeypatch):
    monkeypatch.setenv("TEST_KEY", "abc123")
    assert auth_headers("TEST_KEY") == {"Authorization": "Bearer abc123"}


def test_missing_key_exits_without_leaking(monkeypatch):
    monkeypatch.delenv("TEST_KEY", raising=False)
    with pytest.raises(SystemExit, match="TEST_KEY is not set"):
        auth_headers("TEST_KEY")


def test_post_sends_extra_headers(monkeypatch):
    seen = {}

    class Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_urlopen(req, timeout):
        seen.update(req.header_items())
        return Resp(b"{}")

    monkeypatch.setattr(harness.urllib.request, "urlopen", fake_urlopen)
    harness.post("https://x", "/api/chat", {}, headers={"Authorization": "Bearer k"})
    assert seen["Authorization"] == "Bearer k"
    assert seen["Content-type"] == "application/json"


def test_bakeoff_placeholder_expands_to_harness_dir(tmp_path):
    (tmp_path / "task.json").write_text(json.dumps({"test_cmd": ["{bakeoff}/tools/phpunit", "-c", "x.xml"]}))
    assert load_task_config(tmp_path)["test_cmd"] == [str(HERE / "tools/phpunit"), "-c", "x.xml"]
# <AI-Generated END>
