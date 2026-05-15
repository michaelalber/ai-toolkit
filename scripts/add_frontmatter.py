#!/usr/bin/env python3
"""
Add audience:, source:, and source_commit: frontmatter fields to all SKILL.md files.
- audience: team  → skills/team/*/SKILL.md
- audience: personal → skills/personal/*/SKILL.md
- source + source_commit + source_note → Matt-derived skills per .matt-pocock-attribution.yml
Inserts after the name: line. Does NOT clobber existing audience: fields.
"""
import re
import sys
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = REPO_ROOT / ".matt-pocock-attribution.yml"

def load_manifest() -> dict[str, dict]:
    with open(MANIFEST_PATH) as f:
        data = yaml.safe_load(f)
    return {entry["skill"]: entry for entry in data.get("attributions", [])}


def parse_frontmatter(text: str) -> tuple[str, str, str]:
    """Return (pre_fence, yaml_block, rest). pre_fence includes the opening ---."""
    if not text.startswith("---"):
        return "", "", text
    end = text.find("\n---", 3)
    if end == -1:
        return "", "", text
    yaml_block = text[3:end].strip()
    rest = text[end + 4:]   # skip closing ---
    return "---", yaml_block, rest


def inject_fields(yaml_block: str, audience: str, attribution: dict | None) -> str:
    lines = yaml_block.splitlines()
    out = []
    name_inserted = False

    for line in lines:
        out.append(line)
        if not name_inserted and re.match(r'^name\s*:', line):
            # Skip if audience already present
            if not any(re.match(r'^audience\s*:', l) for l in lines):
                out.append(f"audience: {audience}")
            if attribution:
                out.append(f"source: {attribution['source']}")
                out.append(f"source_commit: {attribution['source_commit']}")
                if attribution.get("locally_modified"):
                    out.append(
                        'source_note: "Modified locally — see .matt-pocock-attribution.yml for details"'
                    )
            name_inserted = True

    return "\n".join(out)


def process_skill(path: Path, audience: str, attribution: dict | None) -> bool:
    text = path.read_text(encoding="utf-8")
    _pre, yaml_block, rest = parse_frontmatter(text)
    if not yaml_block:
        print(f"  SKIP (no frontmatter): {path}", file=sys.stderr)
        return False

    # Already has audience — skip unless attribution fields are missing for Matt skills
    already_has_audience = any(re.match(r'^audience\s*:', l) for l in yaml_block.splitlines())
    already_has_source = any(re.match(r'^source\s*:', l) for l in yaml_block.splitlines())

    needs_audience = not already_has_audience
    needs_source = attribution is not None and not already_has_source

    if not needs_audience and not needs_source:
        return False  # nothing to do

    new_yaml = inject_fields(yaml_block, audience, attribution if needs_source else None)
    new_text = f"---\n{new_yaml}\n---{rest}"
    path.write_text(new_text, encoding="utf-8")
    return True


def main():
    manifest = load_manifest()
    changed = 0

    for audience in ("team", "personal"):
        skill_dir = REPO_ROOT / "skills" / audience
        for skill_path in sorted(skill_dir.glob("*/SKILL.md")):
            skill_name = skill_path.parent.name
            attribution = manifest.get(skill_name)
            if process_skill(skill_path, audience, attribution):
                print(f"  updated: {skill_path.relative_to(REPO_ROOT)}")
                changed += 1

    print(f"\nDone. {changed} files updated.")


if __name__ == "__main__":
    main()
