"""Builders for synthetic skill trees.

Fixtures are built rather than checked in: a rule's red test then shows the *exact*
deviation that trips it, instead of hiding it in a file the reader has to go open.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

CANONICAL_BODY = """\
# Good Full

> "An epigraph that says something."

## Core Philosophy

Why this skill exists, in a sentence or two.

**Non-Negotiable Constraints:**
1. FIRST — do the first thing.
2. SECOND — do the second thing.
3. THIRD — do the third thing.

Depth lives in `references/conventions.md`.

## Workflow

```
DETECT   Read the thing. No files written.
ACT      Do the thing.
VERIFY   Prove it with a captured command result.
```

**Exit criteria:** the thing is done and proven.

## State Block

```
<good-full-state>
phase: DETECT | ACT | VERIFY | COMPLETE
last_action: [description]
next_action: [description]
</good-full-state>
```

## Output Template

See `references/conventions.md` for the report format and `references/templates.md` for
the code templates.

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
"""
# The canonical body names no sibling on purpose: most tests write one skill into an
# otherwise empty tree, and a cross-reference there is an unresolvable target (SK050),
# not a clean skill. Tests for SK050/SK051 build their own tables.

# Padded past the 100-line minimal ceiling so this fixture is genuinely FULL tier — the
# structural rules (SK021-SK026, SK030) only apply there, and a fixture that classifies
# MINIMAL would silently exempt itself from the rules it exists to exercise.
CANONICAL_BODY += "\n" + "\n".join(
    f"Supplementary note {i}: context the skill carries inline." for i in range(60)
)

MINIMAL_BODY = """\
# Good Minimal

Do the narrow thing. Read `references/notes.md` for the detail.

Run these steps in order. Do not skip ahead.

1. Read the input file named by the user.
2. Confirm it parses; stop and report if it does not.
3. Transform it according to the mapping in `references/notes.md`.
4. Write the result next to the input, never over it.
5. Report what changed, as a captured command result.

If the input is missing, say so and stop — do not invent one.
If the mapping has no entry for a field, leave the field untouched and list it.
If the output path already exists, stop and ask before overwriting.

Report the count of fields transformed, the count skipped, and the output path.
"""

TINY_BODY = """\
# Tiny Shim

Ask the user one question at a time. Wait for an answer before the next one.
"""


def write_skill(
    skills_dir: Path,
    name: str,
    *,
    body: str | None = None,
    frontmatter: dict | str | None = None,
    references: dict[str, str] | None = None,
    raw: str | None = None,
) -> Path:
    """Create ``skills_dir/<name>/SKILL.md`` (+ optional references/) and return the dir."""
    skill_dir = skills_dir / name
    skill_dir.mkdir(parents=True, exist_ok=True)

    if raw is not None:
        (skill_dir / "SKILL.md").write_text(raw)
    else:
        fm = frontmatter if frontmatter is not None else {
            "name": name,
            "audience": "team",
            "description": (
                f"Does the {name} thing. Use when you need the {name} thing done. "
                f"Do NOT use when you need something else."
            ),
        }
        if isinstance(fm, dict):
            fm_text = "\n".join(f"{k}: {v}" for k, v in fm.items())
        else:
            fm_text = fm
        (skill_dir / "SKILL.md").write_text(f"---\n{fm_text}\n---\n\n{body or CANONICAL_BODY}")

    if references:
        ref_dir = skill_dir / "references"
        ref_dir.mkdir(exist_ok=True)
        for fname, content in references.items():
            (ref_dir / fname).write_text(content)
    return skill_dir


def filler(lines: int = 30) -> str:
    """A reference file long enough not to read as a stub."""
    return "\n".join(f"Line {i} of substantive reference content." for i in range(lines))


def write_good_full(skills_dir: Path, name: str = "good-full", **kwargs) -> Path:
    body = kwargs.pop("body", CANONICAL_BODY.replace("good-full", name))
    references = kwargs.pop(
        "references", {"conventions.md": filler(), "templates.md": filler()}
    )
    return write_skill(skills_dir, name, body=body, references=references, **kwargs)


def write_good_minimal(skills_dir: Path, name: str = "good-minimal", **kwargs) -> Path:
    references = kwargs.pop("references", {"notes.md": filler()})
    return write_skill(skills_dir, name, body=MINIMAL_BODY, references=references, **kwargs)


def write_tiny(skills_dir: Path, name: str = "tiny-shim", **kwargs) -> Path:
    return write_skill(skills_dir, name, body=TINY_BODY, **kwargs)


@pytest.fixture
def skills_dir(tmp_path: Path) -> Path:
    d = tmp_path / "skills"
    d.mkdir()
    return d


@pytest.fixture
def clean_corpus(skills_dir: Path) -> Path:
    """Three skills, one per tier, all of which must lint clean."""
    write_good_full(skills_dir)
    write_good_minimal(skills_dir)
    write_tiny(skills_dir)
    return skills_dir


def dedent(text: str) -> str:
    return textwrap.dedent(text).lstrip("\n")
