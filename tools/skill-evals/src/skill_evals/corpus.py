# <AI-Generated START>
"""Discovery and parsing of the skill corpus.

A ``Skill`` is a parsed ``skills/<name>/SKILL.md`` plus whatever sits in its
``references/``. Everything the rules need is computed once, here, so a rule is a pure
function of a ``Skill`` rather than a file-reading grep.

Frontmatter is parsed as YAML, never grepped. Several skills legitimately use ``audience:``
and other frontmatter-looking keys *inside their state blocks*; a grep would flag those as
malformed frontmatter, which they are not.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

import yaml

SKILL_FILE = "SKILL.md"

_FENCE = re.compile(r"^\s*(```|~~~)")
_HEADING = re.compile(r"^##\s+(.+?)\s*$")
_STATE_OPEN = re.compile(r"<([a-z0-9]+(?:-[a-z0-9]+)*-state)>")
_REFERENCE_POINTER = re.compile(r"(?<![\w/-])(references/[\w./-]+\.md)")
_TABLE_FIRST_CELL = re.compile(r"^\|\s*`([^`]+)`\s*\|")
_BACKTICKED = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`")


@dataclass(frozen=True)
class Pointer:
    """A ``references/...`` path named in a SKILL.md, with where it was named."""

    target: str
    line: int


@dataclass
class Skill:
    name: str
    """The directory name — the identity Claude Code actually resolves."""

    path: Path
    text: str
    frontmatter: dict | None
    body: str
    body_start_line: int

    _refs: list[Path] = field(default_factory=list)

    # --- frontmatter accessors (None-safe: SK001 reports the missing block) ---

    @property
    def declared_name(self) -> str | None:
        return self._fm_str("name")

    @property
    def description(self) -> str:
        return self._fm_str("description") or ""

    @property
    def audience(self) -> str | None:
        return self._fm_str("audience")

    @property
    def frontmatter_keys(self) -> set[str]:
        return set(self.frontmatter or {})

    def _fm_str(self, key: str) -> str | None:
        value = (self.frontmatter or {}).get(key)
        return None if value is None else str(value).strip()

    # --- structure ---

    @property
    def skill_md(self) -> Path:
        return self.path / SKILL_FILE

    @property
    def lines(self) -> list[str]:
        return self.text.splitlines()

    @property
    def line_count(self) -> int:
        return len(self.lines)

    @cached_property
    def sections(self) -> list[str]:
        """``##`` headings in document order, ignoring any inside a fenced block."""
        return [name for _, name in self._headings]

    @cached_property
    def _headings(self) -> list[tuple[int, str]]:
        found: list[tuple[int, str]] = []
        for lineno, line in _outside_fences(self.lines):
            match = _HEADING.match(line)
            if match:
                found.append((lineno, match.group(1)))
        return found

    @cached_property
    def state_tags(self) -> list[str]:
        """Distinct ``<x-state>`` tags opened anywhere in the file, in first-seen order."""
        seen: list[str] = []
        for tag in _STATE_OPEN.findall(self.text):
            if tag not in seen:
                seen.append(tag)
        return seen

    @cached_property
    def reference_pointers(self) -> list[Pointer]:
        """Every ``references/<file>`` path named in the body, with its line number."""
        pointers: list[Pointer] = []
        for lineno, line in enumerate(self.lines, start=1):
            for target in _REFERENCE_POINTER.findall(line):
                pointers.append(Pointer(target=target, line=lineno))
        return pointers

    @property
    def reference_files(self) -> list[Path]:
        return list(self._refs)

    @cached_property
    def integration_targets(self) -> list[str]:
        """Backticked names in the **first column** of the Integration table.

        Restricting to the first column is what makes the cross-reference rule precise:
        the relationship column legitimately name-drops tools, agents, and sibling skills
        that are not themselves rows.
        """
        section = self.section_lines("Integration")
        targets: list[str] = []
        for line in section:
            match = _TABLE_FIRST_CELL.match(line)
            if match:
                for name in match.group(1).split("/"):
                    name = name.strip()
                    if name and name not in targets:
                        targets.append(name)
        return targets

    @cached_property
    def backticked_slugs(self) -> set[str]:
        """Every backticked kebab-case token in the file — candidate skill references."""
        return set(_BACKTICKED.findall(self.text))

    def section_lines(self, prefix: str) -> list[str]:
        """The lines under the first ``##`` heading starting with ``prefix``."""
        start = None
        for lineno, name in self._headings:
            if start is None and name.startswith(prefix):
                start = lineno
            elif start is not None:
                return self.lines[start : lineno - 1]
        if start is None:
            return []
        return self.lines[start:]

    def has_section(self, prefix: str) -> bool:
        return any(name.startswith(prefix) for name in self.sections)


def parse_frontmatter(text: str) -> tuple[dict | None, str, int]:
    """Split a YAML frontmatter block off the top of ``text``.

    Returns ``(mapping, body, closing_fence_line)``. The mapping is ``None`` when the block
    is absent, unterminated, invalid YAML, or not a mapping — every one of which SK001
    reports rather than crashing on.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text, 0
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            block = "\n".join(lines[1:idx])
            try:
                parsed = yaml.safe_load(block)
            except yaml.YAMLError:
                return None, text, 0
            if not isinstance(parsed, dict):
                return None, text, 0
            body = "\n".join(lines[idx + 1 :])
            return parsed, body, idx + 1
    return None, text, 0


def load_skill(path: str | Path) -> Skill:
    path = Path(path)
    text = (path / SKILL_FILE).read_text()
    frontmatter, body, body_start = parse_frontmatter(text)
    refs_dir = path / "references"
    refs = sorted(p for p in refs_dir.rglob("*") if p.is_file()) if refs_dir.is_dir() else []
    return Skill(
        name=path.name,
        path=path,
        text=text,
        frontmatter=frontmatter,
        body=body,
        body_start_line=body_start,
        _refs=refs,
    )


def discover(skills_dir: str | Path) -> list[Skill]:
    """Every ``skills/<name>/SKILL.md``, one level deep only.

    One level is not a simplification — Claude Code itself only discovers skills at that
    depth, so a skill nested any deeper would never load.
    """
    skills_dir = Path(skills_dir)
    if not skills_dir.is_dir():
        raise FileNotFoundError(f"no such skills directory: {skills_dir}")
    return [
        load_skill(child)
        for child in sorted(skills_dir.iterdir())
        if child.is_dir() and (child / SKILL_FILE).is_file()
    ]


def _outside_fences(lines: list[str]):
    """Yield ``(1-indexed lineno, line)`` for lines that are not inside a code fence."""
    in_fence = False
    for lineno, line in enumerate(lines, start=1):
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield lineno, line
# <AI-Generated END>
