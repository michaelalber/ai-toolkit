# <AI-Generated START>
"""SK060-SK065 — the three global instruction files (Claude Code, OpenCode, Pi).

The globals share one CORE block, delimited by ``<!-- core:start -->`` /
``<!-- core:end -->`` and kept byte-identical, plus a short harness section each. They are
public templates sent with every request, so size, agent-loop safety, and the absence of
personal details are all checked here. Every rule is silent when no global file exists,
so fixture repos built for other rules are unaffected.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..findings import Finding, Severity
from . import rule

GLOBALS = {
    "claude": "claude/global/CLAUDE.md",
    "opencode": "opencode/global/AGENTS.md",
    "pi": "pi/global/AGENTS.md",
}
# Bytes. Pi carries local models only; Claude Code mostly frontier models.
BUDGETS = {"claude": 8192, "opencode": 6144, "pi": 4096}
GLOBAL_DIRS = ("claude/global", "opencode/global", "pi/global")
REFERENCING_FILES = ("scripts/install-claude.sh", "scripts/install-opencode.sh",
                     "scripts/install-pi.sh", "scripts/install-claude.ps1",
                     "scripts/install-opencode.ps1", "scripts/install-pi.ps1", "README.md")

_CORE = re.compile(r"<!-- core:start -->\n(.*?)<!-- core:end -->", re.S)
# A confirmation gate is fine only when the same line scopes it to a mode.
_GATE = re.compile(r"do not (?:begin|start|proceed)|wait for confirmation", re.I)
_PRIVATE_IP = re.compile(r"\b(?:192\.168|10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b")
_GLOBAL_PATH = re.compile(r"\b((?:claude|opencode|pi)/global/[\w./-]*[\w-])")


def _present(ctx) -> dict[str, tuple[Path, str]]:
    root = Path(ctx.repo_root) if ctx.repo_root else None
    if root is None:
        return {}
    out = {}
    for name, rel in GLOBALS.items():
        p = root / rel
        if p.is_file():
            out[name] = (p, p.read_text())
    return out


def _err(rule_id, message, file=None, line=None):
    return Finding(rule_id, Severity.ERROR, message, None, file, line, None)


@rule("SK060", severity=Severity.ERROR, scope="repo",
      summary="each global instruction file has exactly one CORE block")
def sk060_core_block_present(skills, ctx):
    for name, (path, text) in _present(ctx).items():
        n = len(_CORE.findall(text))
        if n != 1:
            yield _err("SK060", f"{GLOBALS[name]} has {n} core blocks; expected exactly one "
                                "<!-- core:start --> … <!-- core:end -->", path)


@rule("SK061", severity=Severity.ERROR, scope="repo",
      summary="the CORE block is byte-identical across the global files")
def sk061_core_identical(skills, ctx):
    cores = {name: _CORE.findall(text) for name, (_, text) in _present(ctx).items()}
    cores = {name: found[0] for name, found in cores.items() if len(found) == 1}
    if len(cores) < 2:
        return
    # The Pi core is the tested baseline; compare everything else against it.
    reference = "pi" if "pi" in cores else sorted(cores)[0]
    for name, core in cores.items():
        if name != reference and core != cores[reference]:
            yield _err("SK061", f"{GLOBALS[name]} core block differs from "
                                f"{GLOBALS[reference]}")


@rule("SK062", severity=Severity.ERROR, scope="repo",
      summary="global instruction files stay within their size budget")
def sk062_size_budget(skills, ctx):
    for name, (path, text) in _present(ctx).items():
        size = len(text.encode())
        if size > BUDGETS[name]:
            yield _err("SK062", f"{GLOBALS[name]} is {size} bytes; budget is "
                                f"{BUDGETS[name]} (sent with every request)", path)


@rule("SK063", severity=Severity.ERROR, scope="repo",
      summary="no unconditional confirmation gate (stalls non-interactive runs)")
def sk063_no_confirmation_gate(skills, ctx):
    for name, (path, text) in _present(ctx).items():
        for lineno, line in enumerate(text.splitlines(), start=1):
            lowered = line.lower()
            if _GATE.search(line) and "confirm" in lowered and "interactive" not in lowered:
                yield _err("SK063", f"{GLOBALS[name]}:{lineno} unconditional confirmation "
                                    f"gate: {line.strip()[:80]!r}", path, lineno)


@rule("SK064", severity=Severity.ERROR, scope="repo",
      summary="public global templates carry no private addresses or blocklisted terms")
def sk064_no_personal_strings(skills, ctx):
    if not _present(ctx):
        return
    root = Path(ctx.repo_root)
    terms = _private_terms(ctx.private_blocklist)
    for rel_dir in GLOBAL_DIRS:
        base = root / rel_dir
        if not base.is_dir():
            continue
        for path in sorted(p for p in base.rglob("*") if p.is_file()):
            text = path.read_text(errors="ignore")
            rel = path.relative_to(root).as_posix()
            for ip in sorted(set(_PRIVATE_IP.findall(text))):
                yield _err("SK064", f"{rel} contains private address {ip}", path)
            lowered = text.lower()
            for term in terms:
                if term.lower() in lowered:
                    # The term itself is private: report the file, never echo the term.
                    yield _err("SK064", f"{rel} contains a term from the private blocklist", path)


@rule("SK065", severity=Severity.ERROR, scope="repo",
      summary="paths into */global/ named by docs and install scripts exist")
def sk065_global_paths_exist(skills, ctx):
    if not _present(ctx):
        return
    root = Path(ctx.repo_root)
    sources = [root / f for f in REFERENCING_FILES]
    for rel_dir in GLOBAL_DIRS:
        base = root / rel_dir
        if base.is_dir():
            sources += [p for p in base.rglob("*") if p.is_file()]
    seen = set()
    for src in sources:
        if not src.is_file():
            continue
        for target in _GLOBAL_PATH.findall(src.read_text(errors="ignore")):
            if (src, target) in seen or (root / target).exists():
                continue
            seen.add((src, target))
            yield _err("SK065", f"{src.relative_to(root).as_posix()} names {target}, "
                                "which does not exist", src)


def _private_terms(path) -> list[str]:
    """Terms from a private blocklist file kept OUTSIDE the repo (one per line, # comments)."""
    if not path:
        return []
    p = Path(path).expanduser()
    if not p.is_file():
        return []
    return [t.strip() for t in p.read_text().splitlines() if t.strip() and not t.startswith("#")]
# <AI-Generated END>
