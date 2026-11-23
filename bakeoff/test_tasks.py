# <AI-Generated START>
"""Eval hygiene: every task's tests must FAIL on the stub and PASS on the reference solution."""
import shutil
from pathlib import Path

import pytest
from harness import hidden_passed, load_hidden, load_task_config
from sandbox import Sandbox

HERE = Path(__file__).parent
TASKS = ["bugfix", "refactor", "feature", "hard_debug", "hard_refactor", "hard_spec",
         "hard_cs_ledger", "hard_py_jobs", "hard_php_booking"]


def _prepare(tmp_path, task, with_reference):
    shutil.copytree(HERE / "tasks" / task, tmp_path, dirs_exist_ok=True)
    if with_reference:
        shutil.copytree(HERE / "reference" / task, tmp_path, dirs_exist_ok=True)
    cfg = load_task_config(HERE / "tasks" / task)
    return Sandbox(tmp_path, cfg["test_cmd"], cfg["test_timeout"])


@pytest.mark.parametrize("task", TASKS)
def test_stub_fails(tmp_path, task):
    assert _prepare(tmp_path, task, False).run_tests()[0] is False


@pytest.mark.parametrize("task", TASKS)
def test_reference_passes(tmp_path, task):
    passed, out = _prepare(tmp_path, task, True).run_tests()
    assert passed, out


HIDDEN = ["hard_debug", "hard_refactor", "hard_spec", "hard_cs_ledger", "hard_py_jobs", "hard_php_booking"]


@pytest.mark.parametrize("task", HIDDEN)
def test_reference_passes_hidden_tests(tmp_path, task):
    sb = _prepare(tmp_path, task, True)
    for rel, data in load_hidden(task).items():  # write directly to see the failure output
        (tmp_path / rel).write_bytes(data)
    passed, out = sb.run_tests()
    assert passed, out


@pytest.mark.parametrize("task", HIDDEN)
def test_stub_fails_hidden_tests(tmp_path, task):
    assert hidden_passed(_prepare(tmp_path, task, False), load_hidden(task)) is False


def test_every_harness_task_has_hidden_tests():
    from harness import TASKS as RUN_TASKS
    assert set(RUN_TASKS) <= set(HIDDEN)
# <AI-Generated END>
