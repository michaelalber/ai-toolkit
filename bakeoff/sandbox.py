# <AI-Generated START>
"""Workdir-confined tools the model may call. Model-supplied paths are untrusted input."""
import subprocess
import sys
from pathlib import Path

IGNORED = {"__pycache__", ".pytest_cache", "bin", "obj"}
PYTEST_CMD = [sys.executable, "-m", "pytest", "-q", "-x", "--tb=short", "-p", "no:cacheprovider"]


class Sandbox:
    def __init__(self, root, test_cmd=None, test_timeout=60):
        self.root = Path(root).resolve()
        self.test_cmd = test_cmd or PYTEST_CMD
        self.test_timeout = test_timeout

    def _safe(self, rel):
        p = (self.root / rel).resolve()
        if not p.is_relative_to(self.root):
            raise ValueError("path escapes workdir")
        return p

    def read_file(self, path):
        return self._safe(path).read_text()

    def write_file(self, path, content):
        p = self._safe(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return f"wrote {len(content)} chars to {path}"

    def list_files(self):
        rels = (p.relative_to(self.root) for p in self.root.rglob("*") if p.is_file())
        return "\n".join(sorted(str(r) for r in rels if not IGNORED & set(r.parts)))

    def run_tests(self):
        """Returns (passed, output). shortcut: runs model-written code unsandboxed beyond cwd+timeout; use a container if tasks ever touch untrusted input."""
        try:
            r = subprocess.run(self.test_cmd, cwd=self.root, capture_output=True, text=True,
                               timeout=self.test_timeout)
        except subprocess.TimeoutExpired:
            return False, "TIMEOUT"
        return r.returncode == 0, (r.stdout + r.stderr)[-3000:]

    def call(self, name, args):
        """Dispatch a tool call; returns (text, is_error)."""
        try:
            if name == "read_file":
                return self.read_file(args["path"]), False
            if name == "write_file":
                return self.write_file(args["path"], args["content"]), False
            if name == "list_files":
                return self.list_files(), False
            if name == "run_tests":
                return self.run_tests()[1], False
        except Exception as e:  # model input is untrusted; report, never crash the run
            return f"ERROR: {e}", True
        return f"ERROR: unknown tool {name}", True
# <AI-Generated END>
