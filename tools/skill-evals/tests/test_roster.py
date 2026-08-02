from pathlib import Path

import pytest
from conftest import write_good_full

from skill_evals import roster
from skill_evals.corpus import discover


def _corpus(skills_dir: Path, n: int = 6):
    for i in range(n):
        write_good_full(
            skills_dir, f"skill-{i}",
            frontmatter={"name": f"skill-{i}", "audience": "team",
                         "description": f"Does thing {i}. Use when thing {i}. Not for others."},
        )
    return discover(skills_dir)


def test_roster_lists_name_and_description(skills_dir: Path):
    skills = _corpus(skills_dir, 2)
    text = roster.build(skills).text
    assert "- skill-0: Does thing 0." in text
    assert "- skill-1:" in text


def test_roster_is_sorted_and_byte_stable(skills_dir: Path):
    skills = _corpus(skills_dir, 4)
    first = roster.build(skills)
    second = roster.build(list(reversed(skills)))
    assert first.text == second.text
    assert first.sha256 == second.sha256


def test_roster_sha_changes_when_a_description_changes(skills_dir: Path):
    before = roster.build(_corpus(skills_dir, 2)).sha256
    write_good_full(
        skills_dir, "skill-0",
        frontmatter={"name": "skill-0", "audience": "team",
                     "description": "Completely different now. Use when. Not for."},
    )
    assert roster.build(discover(skills_dir)).sha256 != before


def test_roster_collapses_folded_description_whitespace(skills_dir: Path):
    write_good_full(
        skills_dir, "s",
        frontmatter={"name": "s", "audience": "team",
                     "description": "|\n  First line.\n  Second line."},
    )
    text = roster.build(discover(skills_dir)).text
    assert text.count("\n") == 0  # one skill, one line


def test_system_prompt_carries_the_roster_and_the_json_contract(skills_dir: Path):
    prompt = roster.build(_corpus(skills_dir, 2)).system_prompt()
    assert "- skill-0:" in prompt
    assert '"skill"' in prompt and '"runner_up"' in prompt
    assert "none" in prompt


def test_unknown_mode_is_rejected(skills_dir: Path):
    with pytest.raises(ValueError):
        roster.build(_corpus(skills_dir, 1), mode="sideways")


# --- truncated mode: the ablation --------------------------------------------------


def test_truncated_mode_drops_the_negative_boundary(skills_dir: Path):
    write_good_full(
        skills_dir, "s",
        frontmatter={"name": "s", "audience": "team",
                     "description": "Scaffolds crates. Use when publishing. Do NOT use for apps."},
    )
    skills = discover(skills_dir)
    assert "Do NOT use" in roster.build(skills, mode=roster.FULL).text
    assert "Do NOT use" not in roster.build(skills, mode=roster.TRUNCATED).text


def test_truncated_mode_keeps_the_first_two_sentences(skills_dir: Path):
    write_good_full(
        skills_dir, "s",
        frontmatter={"name": "s", "audience": "team",
                     "description": "One. Two. Three. Not for four."},
    )
    text = roster.build(discover(skills_dir), mode=roster.TRUNCATED).text
    assert "One. Two." in text and "Three." not in text


# --- shard mode --------------------------------------------------------------------


def test_shard_mode_partitions_the_corpus(skills_dir: Path):
    skills = _corpus(skills_dir, 6)
    sizes = [len(roster.build(skills, mode=roster.SHARD, shards=3, shard_index=i).names)
             for i in range(3)]
    assert sizes == [2, 2, 2]


def test_shards_are_disjoint_and_cover_everything(skills_dir: Path):
    skills = _corpus(skills_dir, 6)
    seen = []
    for i in range(3):
        seen += list(roster.build(skills, mode=roster.SHARD, shards=3, shard_index=i).names)
    assert sorted(seen) == sorted(s.name for s in skills)


def test_shard_is_deterministic(skills_dir: Path):
    skills = _corpus(skills_dir, 6)
    a = roster.build(skills, mode=roster.SHARD, shards=3, shard_index=1)
    b = roster.build(skills, mode=roster.SHARD, shards=3, shard_index=1)
    assert a.names == b.names


def test_shard_always_includes_the_expected_skill(skills_dir: Path):
    """Otherwise a sharded run scores a case the model could not have got right."""
    skills = _corpus(skills_dir, 6)
    for i in range(3):
        r = roster.build(skills, mode=roster.SHARD, shards=3, shard_index=i,
                         must_include="skill-5")
        assert "skill-5" in r.names


def test_shard_does_not_duplicate_an_already_present_skill(skills_dir: Path):
    skills = _corpus(skills_dir, 6)
    r = roster.build(skills, mode=roster.SHARD, shards=3, shard_index=1,
                     must_include=roster.build(skills, mode=roster.SHARD, shards=3,
                                               shard_index=1).names[0])
    assert len(r.names) == len(set(r.names))


def test_zero_shards_is_rejected(skills_dir: Path):
    with pytest.raises(ValueError):
        roster.build(_corpus(skills_dir, 2), mode=roster.SHARD, shards=0)


# --- disable-model-invocation is withheld, as the harness does ---------------------


def _with_grill(skills_dir: Path):
    _corpus(skills_dir, 2)
    write_good_full(
        skills_dir, "grill-me",
        frontmatter={"name": "grill-me", "audience": "team", "disable-model-invocation": "true",
                     "description": "Interviews you. Use when grilling. Not for building."},
    )
    return discover(skills_dir)


def test_non_invocable_skills_are_withheld_by_default(skills_dir: Path):
    r = roster.build(_with_grill(skills_dir))
    assert "grill-me" not in r.names
    assert "- grill-me:" not in r.text


def test_withheld_skills_are_recorded(skills_dir: Path):
    assert roster.build(_with_grill(skills_dir)).withheld == ("grill-me",)


def test_non_invocable_skills_can_be_included_deliberately(skills_dir: Path):
    r = roster.build(_with_grill(skills_dir), include_non_invocable=True)
    assert "grill-me" in r.names
    assert r.withheld == ()


def test_is_non_invocable_reads_the_frontmatter_flag(skills_dir: Path):
    skills = {s.name: s for s in _with_grill(skills_dir)}
    assert roster.is_non_invocable(skills["grill-me"])
    assert not roster.is_non_invocable(skills["skill-0"])


def test_withholding_changes_the_roster_sha(skills_dir: Path):
    skills = _with_grill(skills_dir)
    assert roster.build(skills).sha256 != roster.build(
        skills, include_non_invocable=True
    ).sha256


# --- candidate pairs ---------------------------------------------------------------


def test_candidate_pairs_rank_similar_descriptions_first(skills_dir: Path):
    common = ("Conducts an OWASP security review of {} applications. "
              "Use when auditing {} for vulnerabilities. Not for architecture grading.")
    for lang in ("python", "rust"):
        write_good_full(
            skills_dir, f"{lang}-security-review",
            frontmatter={"name": f"{lang}-security-review", "audience": "team",
                         "description": common.format(lang, lang)},
        )
    write_good_full(
        skills_dir, "para-file",
        frontmatter={"name": "para-file", "audience": "team",
                     "description": "Files a document into Projects, Areas, Resources, "
                                    "Archives. Use when sorting an inbox. Not for review."},
    )
    top = roster.candidate_pairs(discover(skills_dir), top=1)[0]
    assert {top[0], top[1]} == {"python-security-review", "rust-security-review"}


def test_candidate_pairs_are_deterministic(skills_dir: Path):
    skills = _corpus(skills_dir, 5)
    assert roster.candidate_pairs(skills, top=5) == roster.candidate_pairs(skills, top=5)


def test_candidate_pairs_respects_top_n(skills_dir: Path):
    assert len(roster.candidate_pairs(_corpus(skills_dir, 6), top=4)) == 4
