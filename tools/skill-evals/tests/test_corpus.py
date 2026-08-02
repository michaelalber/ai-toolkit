from pathlib import Path

import pytest
from conftest import write_good_full, write_skill

from skill_evals.corpus import discover, load_skill, parse_frontmatter


def test_parse_frontmatter_returns_mapping_body_and_offset():
    text = "---\nname: x\naudience: team\n---\n\n# Title\n\nbody\n"
    fm, body, body_line = parse_frontmatter(text)
    assert fm == {"name": "x", "audience": "team"}
    assert body.startswith("\n# Title")
    assert body_line == 4  # 1-indexed line of the closing ---


def test_parse_frontmatter_missing_block_returns_none():
    fm, body, _ = parse_frontmatter("# Title\n\nno frontmatter here\n")
    assert fm is None
    assert "no frontmatter" in body


def test_parse_frontmatter_unterminated_block_returns_none():
    fm, _, _ = parse_frontmatter("---\nname: x\n\n# Title without a closing fence\n")
    assert fm is None


def test_parse_frontmatter_invalid_yaml_returns_none():
    fm, _, _ = parse_frontmatter("---\nname: [unclosed\n---\n\nbody\n")
    assert fm is None


def test_parse_frontmatter_non_mapping_returns_none():
    fm, _, _ = parse_frontmatter("---\n- just\n- a list\n---\n\nbody\n")
    assert fm is None


def test_parse_frontmatter_reads_folded_description():
    text = (
        "---\nname: x\naudience: team\ndescription: >\n  First line.\n  Second line.\n---\n\nbody\n"
    )
    fm, _, _ = parse_frontmatter(text)
    assert fm["description"] == "First line. Second line."


def test_load_skill_exposes_name_description_audience(skills_dir: Path):
    write_good_full(skills_dir, "alpha")
    skill = load_skill(skills_dir / "alpha")
    assert skill.name == "alpha"  # from the directory
    assert skill.declared_name == "alpha"  # from frontmatter
    assert skill.audience == "team"
    assert "alpha" in skill.description


def test_load_skill_counts_lines_of_the_whole_file(skills_dir: Path):
    write_skill(skills_dir, "s", raw="---\nname: s\n---\n\nline\nline\n")
    assert load_skill(skills_dir / "s").line_count == 6


def test_load_skill_lists_sections_in_document_order(skills_dir: Path):
    write_good_full(skills_dir, "alpha")
    sections = load_skill(skills_dir / "alpha").sections
    assert sections == [
        "Core Philosophy",
        "Workflow",
        "State Block",
        "Output Template",
        "Integration with Other Skills",
    ]


def test_sections_ignore_headings_inside_fenced_code(skills_dir: Path):
    """A '## ' inside a fenced template block is content, not structure."""
    body = "# T\n\n## Core Philosophy\n\nx\n\n```\n## Not A Section\n```\n"
    write_good_full(skills_dir, "alpha", body=body)
    assert load_skill(skills_dir / "alpha").sections == ["Core Philosophy"]


def test_load_skill_finds_state_tags(skills_dir: Path):
    write_good_full(skills_dir, "alpha")
    assert load_skill(skills_dir / "alpha").state_tags == ["alpha-state"]


def test_state_tags_are_deduplicated_within_a_file(skills_dir: Path):
    body = (
        "# T\n\n## State Block\n\n```\n<a-state>\nx: 1\n</a-state>\n```\n\n"
        "<a-state>\n</a-state>\n"
    )
    write_good_full(skills_dir, "alpha", body=body)
    assert load_skill(skills_dir / "alpha").state_tags == ["a-state"]


def test_load_skill_lists_reference_files(skills_dir: Path):
    write_good_full(skills_dir, "alpha")
    skill = load_skill(skills_dir / "alpha")
    assert sorted(p.name for p in skill.reference_files) == ["conventions.md", "templates.md"]


def test_reference_files_empty_when_dir_absent(skills_dir: Path):
    write_skill(skills_dir, "bare")
    assert load_skill(skills_dir / "bare").reference_files == []


def test_reference_files_are_found_recursively(skills_dir: Path):
    """qraspi-skeleton keeps an archetypes/ subdirectory of recipes."""
    d = write_good_full(skills_dir, "alpha")
    (d / "references" / "archetypes").mkdir()
    (d / "references" / "archetypes" / "python.md").write_text("x")
    names = {p.name for p in load_skill(d).reference_files}
    assert "python.md" in names


def test_reference_pointers_are_extracted_from_the_body(skills_dir: Path):
    write_good_full(skills_dir, "alpha")
    skill = load_skill(skills_dir / "alpha")
    pointed = {p.target for p in skill.reference_pointers}
    assert pointed == {"references/conventions.md", "references/templates.md"}


def test_reference_pointers_carry_line_numbers(skills_dir: Path):
    write_good_full(skills_dir, "alpha")
    for pointer in load_skill(skills_dir / "alpha").reference_pointers:
        assert pointer.line > 0


def test_integration_targets_read_the_first_column_only(skills_dir: Path):
    body = (
        "# T\n\n## Integration with Other Skills\n\n"
        "| Skill | Relationship |\n|---|---|\n"
        "| `alpha` | Mentions `beta` in the prose column. |\n"
        "| `gamma` | Another. |\n"
    )
    write_good_full(skills_dir, "s", body=body)
    assert load_skill(skills_dir / "s").integration_targets == ["alpha", "gamma"]


def test_integration_targets_empty_without_the_section(skills_dir: Path):
    write_good_full(skills_dir, "s", body="# T\n\n## Workflow\n\n| `x` | y |\n")
    assert load_skill(skills_dir / "s").integration_targets == []


def test_discover_finds_every_skill_sorted(skills_dir: Path):
    for name in ("charlie", "alpha", "bravo"):
        write_good_full(skills_dir, name)
    assert [s.name for s in discover(skills_dir)] == ["alpha", "bravo", "charlie"]


def test_discover_ignores_directories_without_a_skill_md(skills_dir: Path):
    write_good_full(skills_dir, "real")
    (skills_dir / "not-a-skill").mkdir()
    assert [s.name for s in discover(skills_dir)] == ["real"]


def test_discover_does_not_recurse_into_subdirectories(skills_dir: Path):
    """Claude Code only discovers skills/<name>/SKILL.md one level deep."""
    write_good_full(skills_dir, "top")
    nested = skills_dir / "team"
    write_good_full(nested, "buried")
    assert [s.name for s in discover(skills_dir)] == ["top"]


def test_discover_raises_on_a_missing_directory(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        discover(tmp_path / "nope")
