# <AI-Generated START>
"""Code-execution scorer: run model-generated code against hidden tests.

The strongest, least-gameable coding signal. Defense-in-depth sandboxing:
  * isolated temporary working directory (removed after the run)
  * wall-clock timeout (killed on expiry)
  * POSIX resource limits (CPU seconds, file size) via a preexec hook
  * a minimal environment and an isolated interpreter (python -I)
  * a preamble that disables socket creation, so generated code cannot use the network

NOTE: this stops accidental and casual-malicious code. It is NOT a substitute for
OS-level isolation. For untrusted models, run the whole harness inside a container or
firejail. See README > Security.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from .base import ScoreResult, register

try:  # POSIX only; absent on Windows
    import resource
except ImportError:  # pragma: no cover - platform dependent
    resource = None  # type: ignore[assignment]

DEFAULT_TIMEOUT = 10
DEFAULT_FSIZE_BYTES = 10 * 1024 * 1024  # 10 MB of writes

# Disables network access from within the sandboxed script by neutralising socket
# creation. Re-importing `socket` returns this same (mutated) module object.
_NETWORK_GUARD = (
    "import socket as _guard_sock\n"
    "def _blocked(*a, **k):\n"
    "    raise OSError('network disabled in sandbox')\n"
    "_guard_sock.socket = _blocked\n"
)

_FENCE = re.compile(r"```(?:python|py)?\s*(.*?)```", re.DOTALL)


def extract_code(output: str) -> str:
    """Return the code from a fenced block, or the raw output if there is no fence."""
    match = _FENCE.search(output)
    return match.group(1) if match else output


def _child_limits():  # pragma: no cover - runs only in the child process
    if resource is None:
        return
    cpu = int(os.environ.get("_EVAL_CPU_SECONDS", "11"))
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
    resource.setrlimit(resource.RLIMIT_FSIZE, (DEFAULT_FSIZE_BYTES, DEFAULT_FSIZE_BYTES))


@register("code_exec")
def code_exec(output: str, spec: dict, context: dict) -> ScoreResult:
    code = extract_code(output).strip()
    if not code:
        return ScoreResult(0.0, False, "no code found in output")

    timeout = int(spec.get("timeout", DEFAULT_TIMEOUT))
    script = f"{_NETWORK_GUARD}\n{code}\n\n{spec.get('test_code', '')}\n"

    with tempfile.TemporaryDirectory(prefix="ollama-evals-") as workdir:
        script_path = Path(workdir) / "_candidate.py"
        script_path.write_text(script)
        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONIOENCODING": "utf-8",
            "_EVAL_CPU_SECONDS": str(timeout + 1),
        }
        try:
            proc = subprocess.run(
                [sys.executable, "-I", str(script_path)],
                cwd=workdir,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
                preexec_fn=_child_limits if resource is not None else None,
            )
        except subprocess.TimeoutExpired:
            return ScoreResult(0.0, False, f"timeout after {timeout}s")

    if proc.returncode == 0:
        return ScoreResult(1.0, True)
    detail = (proc.stderr or proc.stdout or "").strip()
    return ScoreResult(0.0, False, _tail(detail))


def _tail(text: str, lines: int = 12) -> str:
    return "\n".join(text.splitlines()[-lines:])
# <AI-Generated END>
