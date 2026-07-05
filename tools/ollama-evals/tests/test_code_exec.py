"""Security-critical: the code-execution sandbox. Target >=95% coverage."""

import sys

import pytest

from ollama_evals.scorers.code_exec import code_exec, extract_code

GOOD_SOLUTION = """```python
def is_prime(n):
    if n < 2:
        return False
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
            return False
    return True
```"""

TEST_CODE = """
assert is_prime(7)
assert not is_prime(9)
assert not is_prime(1)
"""


def _spec(test_code=TEST_CODE, timeout=10):
    return {"type": "code_exec", "test_code": test_code, "timeout": timeout}


def test_good_solution_passes():
    r = code_exec(GOOD_SOLUTION, _spec(), {})
    assert r.passed and r.score == 1.0


def test_wrong_solution_fails_with_detail():
    bad = "def is_prime(n):\n    return True\n"
    r = code_exec(bad, _spec(), {})
    assert not r.passed and r.score == 0.0
    assert r.detail


def test_infinite_loop_times_out():
    spinner = "def is_prime(n):\n    while True:\n        pass\n"
    r = code_exec(spinner, _spec(timeout=2), {})
    assert not r.passed
    assert "timeout" in r.detail.lower()


def test_extracts_python_fence():
    assert "def is_prime" in extract_code(GOOD_SOLUTION)
    # raw (unfenced) code passes through unchanged
    assert extract_code("def f(): return 1").strip() == "def f(): return 1"


def test_empty_output_fails():
    r = code_exec("", _spec(), {})
    assert not r.passed
    assert "no code" in r.detail.lower()


@pytest.mark.skipif(sys.platform == "win32", reason="network guard asserted on POSIX CI")
def test_network_is_blocked_in_sandbox():
    net = "def is_prime(n):\n    return True\n"
    probe = "import socket\nsocket.socket()\n"
    r = code_exec(net, _spec(test_code=probe), {})
    assert not r.passed
    assert "network disabled" in r.detail.lower()


def test_syntax_error_in_candidate_fails():
    r = code_exec("def is_prime(n) return n", _spec(), {})
    assert not r.passed
