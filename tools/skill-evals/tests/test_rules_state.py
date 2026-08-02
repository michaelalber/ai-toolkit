from pathlib import Path

from conftest import CANONICAL_BODY, write_good_full

from skill_evals.lint import lint


def _ids(skills_dir: Path, rule: str, **kw) -> list[str]:
    return [f.rule_id for f in lint(skills_dir, only=[rule], **kw)]


def _messages(skills_dir: Path, rule: str, **kw) -> list[str]:
    return [f.message for f in lint(skills_dir, only=[rule], **kw)]


def _with_tag(name: str, tag: str) -> str:
    return CANONICAL_BODY.replace("good-full-state", tag).replace("# Good Full", f"# {name}")


# --- SK030 / SK031 -----------------------------------------------------------------


def test_sk030_flags_a_full_skill_without_a_state_block(skills_dir: Path):
    body = CANONICAL_BODY.replace("<good-full-state>", "").replace("</good-full-state>", "")
    write_good_full(skills_dir, "s", body=body)
    assert _ids(skills_dir, "SK030") == ["SK030"]


def test_sk031_flags_an_unclosed_state_tag(skills_dir: Path):
    body = CANONICAL_BODY.replace("</good-full-state>", "")
    write_good_full(skills_dir, "s", body=body)
    assert "opened but never closed" in _messages(skills_dir, "SK031")[0]


def test_sk031b_flags_a_tag_unrelated_to_the_skill_name(skills_dir: Path):
    write_good_full(skills_dir, "alpha", body=_with_tag("Alpha", "totally-different-state"))
    assert "shares no token" in _messages(skills_dir, "SK031b")[0]


def test_sk031b_accepts_a_tag_sharing_one_token(skills_dir: Path):
    write_good_full(skills_dir, "python-security-review",
                    body=_with_tag("X", "security-review-state"))
    assert _ids(skills_dir, "SK031b") == []


# --- SK032: family ownership -------------------------------------------------------


def _family_pair(skills_dir: Path):
    for name in ("python-security-review", "rust-security-review"):
        write_good_full(skills_dir, name, body=_with_tag(name, "security-review-state"))


def test_sk032_flags_an_undeclared_shared_tag(skills_dir: Path):
    _family_pair(skills_dir)
    messages = _messages(skills_dir, "SK032")
    assert len(messages) == 1
    assert "no declared family" in messages[0]
    assert "python-security-review" in messages[0]


def test_sk032_accepts_a_declared_family(skills_dir: Path):
    _family_pair(skills_dir)
    families = {
        "security-review-state": {
            "skills": ["python-security-review", "rust-security-review"],
            "rationale": "One OWASP workflow per language; the tag names the shared workflow.",
        }
    }
    assert _ids(skills_dir, "SK032", state_tag_families=families) == []


def test_sk032_flags_an_interloper_in_a_declared_family(skills_dir: Path):
    _family_pair(skills_dir)
    write_good_full(skills_dir, "unrelated-thing",
                    body=_with_tag("Unrelated", "security-review-state"))
    families = {
        "security-review-state": {
            "skills": ["python-security-review", "rust-security-review"],
            "rationale": "family",
        }
    }
    findings = lint(skills_dir, only=["SK032"], state_tag_families=families).findings
    assert [f.skill for f in findings] == ["unrelated-thing"]
    assert "does not include" in findings[0].message


def test_sk032_ignores_a_tag_owned_by_one_skill(clean_corpus: Path):
    assert _ids(clean_corpus, "SK032") == []


def test_sk032_ignores_a_tag_repeated_within_one_file(skills_dir: Path):
    """A skill may show its own tag twice — in the State Block and in an example."""
    body = CANONICAL_BODY + "\n<good-full-state>\nphase: COMPLETE\n</good-full-state>\n"
    write_good_full(skills_dir, "good-full", body=body)
    assert _ids(skills_dir, "SK032") == []


# --- SK033: agent collisions -------------------------------------------------------


def test_sk033_flags_an_agent_reusing_a_skill_tag(skills_dir: Path, tmp_path: Path):
    write_good_full(skills_dir, "automated-code-review",
                    body=_with_tag("X", "automated-review-state"))
    agents = tmp_path / "claude" / "agents"
    agents.mkdir(parents=True)
    (agents / "code-review-agent.md").write_text(
        "<automated-review-state>\n</automated-review-state>"
    )
    findings = lint(skills_dir, repo_root=tmp_path, only=["SK033"]).findings
    assert "already owned by skill" in findings[0].message


def test_sk033_allows_an_agent_to_own_its_own_distinct_tag(skills_dir: Path, tmp_path: Path):
    write_good_full(skills_dir, "automated-code-review",
                    body=_with_tag("X", "automated-review-state"))
    agents = tmp_path / "claude" / "agents"
    agents.mkdir(parents=True)
    (agents / "code-review-agent.md").write_text("<code-review-state>\n</code-review-state>")
    assert _ids(skills_dir, "SK033", repo_root=tmp_path) == []


def test_sk033_is_silent_without_an_agents_tree(clean_corpus: Path):
    assert _ids(clean_corpus, "SK033") == []
