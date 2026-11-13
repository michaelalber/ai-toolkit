# <AI-Generated START>
"""SK070-SK073 — agents and commands stay in sync with skills/ and with each other.

Skills are shared by Claude Code, OpenCode and Pi; agents and commands exist twice, once
per runtime, in different formats (Claude ``skills:`` frontmatter, OpenCode
``skill({ name: "..." })`` calls). A skill rename or removal therefore has to land in up
to four places, and the runtime that is missed fails quietly: in OpenCode a stale
``tdd`` resolves to the ``/tdd`` command instead of the ``tdd-loop`` skill.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..findings import Finding, Severity
from ..repo import agent_names
from . import rule
from .crossref import _closest

PLATFORMS = ("claude", "opencode")
LABEL = {"claude": "Claude Code", "opencode": "OpenCode"}
_OPENCODE_CALL = re.compile(r'skill\(\s*\{\s*name:\s*"([^"]+)"')
# Read the `skills:` list directly, not via YAML: agent descriptions routinely carry an
# unquoted `: ` that strict YAML rejects but Claude Code loads, and a failed parse would
# silently report "loads nothing".
_CLAUDE_SKILLS = re.compile(r"^skills:[ \t]*\n((?:[ \t]+-[ \t]*\S.*\n?)+)", re.M)
# A whole backticked slug, not `/tdd` (a command) nor `research-*` (a glob over agents).
_BACKTICKED = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)*)`")


def _agent_file(root: Path, platform: str, name: str) -> Path:
    return root / platform / "agents" / f"{name}.md"


def _loaded_skills(path: Path, platform: str) -> set[str]:
    """Skills an agent declares it loads; placeholders like `<lang>-x` are dropped."""
    text = path.read_text(encoding="utf-8")
    if platform == "claude":
        front = text.split("\n---", 1)[0] if text.startswith("---") else ""
        block = _CLAUDE_SKILLS.search(front)
        lines = block.group(1).splitlines() if block else []
        names = {line.strip()[1:].strip() for line in lines}
    else:
        names = set(_OPENCODE_CALL.findall(text))
    return {n for n in names if "<" not in n}


def _command_names(root: Path, platform: str) -> set[str]:
    base = root / platform / "commands"
    return {p.stem for p in base.glob("*.md")} if base.is_dir() else set()


def _finding(rule_id, severity, message, path, evals_tc="TC2"):
    return Finding(rule_id, severity, message, None, path, None, evals_tc)


@rule("SK070", severity=Severity.ERROR, scope="repo",
      summary="agent skill references resolve to real skills", evals_tc="TC2")
def sk070_agent_skills_resolve(skills, ctx):
    root = ctx.repo_root
    for platform in PLATFORMS:
        for name in sorted(agent_names(root, platform)):
            path = _agent_file(root, platform, name)
            for skill in sorted(_loaded_skills(path, platform) - ctx.skill_names):
                suggestion = _closest(skill, ctx.skill_names)
                hint = f"; did you mean {suggestion!r}?" if suggestion else ""
                yield _finding("SK070", Severity.ERROR,
                               f"{platform} agent {name!r} loads `{skill}`, which is not a "
                               f"skill{hint}", path)


@rule("SK071", severity=Severity.ERROR, scope="repo",
      summary="Claude and OpenCode agent pairs load the same skills", evals_tc="TC2")
def sk071_agent_pairs_load_same_skills(skills, ctx):
    root = ctx.repo_root
    # Unpaired agents are SK058's finding; only compare the ones that exist twice.
    for name in sorted(agent_names(root, "claude") & agent_names(root, "opencode")):
        claude = _loaded_skills(_agent_file(root, "claude", name), "claude")
        opencode = _loaded_skills(_agent_file(root, "opencode", name), "opencode")
        if claude == opencode:
            continue
        parts = []
        if claude - opencode:
            parts.append("Claude Code only: " + ", ".join(sorted(claude - opencode)))
        if opencode - claude:
            parts.append("OpenCode only: " + ", ".join(sorted(opencode - claude)))
        yield _finding("SK071", Severity.ERROR,
                       f"agent {name!r} loads different skills per runtime ({'; '.join(parts)})",
                       _agent_file(root, "opencode", name))


@rule("SK072", severity=Severity.ERROR, scope="repo",
      summary="Claude and OpenCode commands are in parity", evals_tc="TC2")
def sk072_command_parity(skills, ctx):
    root = ctx.repo_root
    claude, opencode = _command_names(root, "claude"), _command_names(root, "opencode")
    for name in sorted(claude - opencode):
        yield _finding("SK072", Severity.ERROR,
                       f"command '/{name}' exists for Claude Code but not OpenCode",
                       root / "opencode" / "commands")
    for name in sorted(opencode - claude):
        yield _finding("SK072", Severity.ERROR,
                       f"command '/{name}' exists for OpenCode but not Claude Code",
                       root / "claude" / "commands")


@rule("SK073", severity=Severity.WARNING, scope="repo",
      summary="agents and commands name no stale skills", evals_tc="TC7")
def sk073_stale_skill_names_in_primitives(skills, ctx):
    """SK052's check, applied to agent and command bodies.

    Two shapes are reported:

    * a hyphenated slug that is not a skill, agent, or `references/` file name but closely
      resembles a skill — a rename's long tail;
    * a bare single word that is a *command* name and prefixes a skill — `tdd` after the
      `tdd` -> `tdd-loop` rename. In OpenCode that name resolves to the `/tdd` command, so
      the skill silently never loads. Other single words (`skill`, `test`) are ordinary
      prose and stay quiet; a command is cited as `/tdd`, which does not match.
    """
    root = ctx.repo_root
    known = ctx.skill_names | ctx.known_non_skills
    reference_files = {p.stem for p in (root / "skills").glob("*/references/**/*.md")}
    for platform in PLATFORMS:
        known_agents = agent_names(root, platform)
        commands = _command_names(root, platform)
        targets = [("agent", n, _agent_file(root, platform, n)) for n in sorted(known_agents)]
        targets += [("command", f"/{n}", root / platform / "commands" / f"{n}.md")
                    for n in sorted(commands)]
        for kind, label, path in targets:
            tokens = set(_BACKTICKED.findall(path.read_text(encoding="utf-8")))
            for token in sorted(tokens - known - known_agents - reference_files):
                if "-" not in token and token not in commands:
                    continue
                suggestion = _closest(token, ctx.skill_names)
                if not suggestion:
                    continue
                what = ("is a command, not a skill; closest skill is" if token in commands
                        else "is not a skill; closest is")
                yield _finding("SK073", Severity.WARNING,
                               f"{platform} {kind} {label!r}: `{token}` {what} `{suggestion}` "
                               "— stale rename?", path, "TC7")
# <AI-Generated END>
