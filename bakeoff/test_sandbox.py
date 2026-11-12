# <AI-Generated START>
import sys

import pytest
from sandbox import Sandbox


def test_write_then_read_roundtrip(tmp_path):
    sb = Sandbox(tmp_path)
    sb.write_file("a/b.py", "x = 1\n")
    assert sb.read_file("a/b.py") == "x = 1\n"


@pytest.mark.parametrize("bad", ["../evil.py", "/etc/passwd", "a/../../evil.py"])
def test_path_escape_is_rejected(tmp_path, bad):
    sb = Sandbox(tmp_path)
    text, is_err = sb.call("write_file", {"path": bad, "content": "x"})
    assert is_err and "escapes" in text


def test_unknown_tool_is_error(tmp_path):
    assert Sandbox(tmp_path).call("rm_rf", {})[1] is True


def test_missing_arg_is_error_not_crash(tmp_path):
    assert Sandbox(tmp_path).call("read_file", {})[1] is True


def test_list_files_ignores_caches(tmp_path):
    sb = Sandbox(tmp_path)
    sb.write_file("m.py", "")
    sb.write_file("__pycache__/m.pyc", "")
    assert sb.list_files() == "m.py"


def test_run_tests_pass_and_fail(tmp_path):
    sb = Sandbox(tmp_path)
    sb.write_file("test_ok.py", "def test_ok(): assert True\n")
    assert sb.run_tests()[0] is True
    sb.write_file("test_bad.py", "def test_bad(): assert False\n")
    assert sb.run_tests()[0] is False


@pytest.mark.parametrize("code,expected", [(0, True), (1, False)])
def test_custom_test_cmd_exit_code_decides_pass(tmp_path, code, expected):
    sb = Sandbox(tmp_path, test_cmd=[sys.executable, "-c", f"import sys; sys.exit({code})"])
    assert sb.run_tests()[0] is expected


def test_slow_test_cmd_times_out(tmp_path):
    sb = Sandbox(tmp_path, [sys.executable, "-c", "import time; time.sleep(5)"], test_timeout=1)
    assert sb.run_tests() == (False, "TIMEOUT")


def test_list_files_ignores_dotnet_build_output(tmp_path):
    sb = Sandbox(tmp_path)
    sb.write_file("App.cs", "")
    sb.write_file("bin/Debug/App.dll", "")
    sb.write_file("obj/project.assets.json", "")
    assert sb.list_files() == "App.cs"
# <AI-Generated END>
