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
