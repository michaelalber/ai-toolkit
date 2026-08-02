from pathlib import Path

import pytest

from skill_evals import rubric as rubric_mod

REPO_ROOT = Path(__file__).resolve().parents[3]
REAL_RUBRIC = REPO_ROOT / rubric_mod.RUBRIC_PATH


@pytest.fixture(scope="module")
def real():
    if not REAL_RUBRIC.is_file():
        pytest.skip("real scoring-rubric.md not present")
    return rubric_mod.load(REAL_RUBRIC)


# --- parsing the real rubric -------------------------------------------------------


def test_parses_all_ten_dimensions(real):
    assert len(real.dimensions) == 10
    assert [d.number for d in real.dimensions] == list(range(1, 11))


def test_each_dimension_has_all_five_criteria(real):
    for d in real.dimensions:
        assert sorted(d.criteria) == [1, 2, 3, 4, 5], f"dimension {d.number}"


def test_dimension_names_and_questions_are_captured(real):
    first = real.dimensions[0]
    assert first.name == "Trigger Precision"
    assert "description:" in first.question


def test_max_total_is_fifty(real):
    assert real.max_total == 50


def test_dimension_keys_are_stable(real):
    assert [d.key for d in real.dimensions][:3] == ["d1", "d2", "d3"]


def test_criteria_table_renders_high_to_low(real):
    table = real.dimensions[0].criteria_table()
    assert table.startswith("5:")
    assert table.strip().splitlines()[-1].startswith("1:")


# --- verdict bands -----------------------------------------------------------------


@pytest.mark.parametrize(
    "total,expected",
    [
        (50, "EXEMPLARY"), (45, "EXEMPLARY"),
        (44, "PASS"), (35, "PASS"),
        (34, "REVISE"), (25, "REVISE"),
        (24, "DEPRECATE"), (0, "DEPRECATE"),
    ],
)
def test_verdict_boundaries(real, total, expected):
    assert real.verdict(total) == expected


def test_thresholds_are_parsed_including_the_open_lower_band(real):
    verdicts = [t.verdict for t in real.thresholds]
    assert verdicts == ["EXEMPLARY", "PASS", "REVISE", "DEPRECATE"]
    deprecate = real.thresholds[-1]
    assert (deprecate.low, deprecate.high) == (0, 24)


def test_sha_changes_with_the_file(tmp_path: Path):
    a = tmp_path / "a.md"
    a.write_text(REAL_RUBRIC.read_text() if REAL_RUBRIC.is_file() else _MINIMAL)
    first = rubric_mod.load(a).sha256
    a.write_text(a.read_text() + "\n<!-- edited -->\n")
    assert rubric_mod.load(a).sha256 != first


def test_by_key_lookup(real):
    assert real.by_key("d5").name.startswith("State Block")
    with pytest.raises(KeyError):
        real.by_key("d99")


# --- error handling ----------------------------------------------------------------


_MINIMAL = """\
| Total | Verdict | Action |
|-------|---------|--------|
| 5–10 | PASS | fine |
| < 5 | FAIL | no |

## Dimension 1 — Only One

Does it work?

| Score | Criteria |
|-------|----------|
| 5 | great |
| 4 | good |
| 3 | ok |
| 2 | poor |
| 1 | bad |
"""


def test_missing_file_raises(tmp_path: Path):
    with pytest.raises(rubric_mod.RubricParseError, match="no scoring rubric"):
        rubric_mod.load(tmp_path / "absent.md")


def test_file_without_dimensions_raises(tmp_path: Path):
    path = tmp_path / "r.md"
    path.write_text("| Total | Verdict | Action |\n|---|---|---|\n| 5–10 | PASS | ok |\n")
    with pytest.raises(rubric_mod.RubricParseError, match="no '## Dimension"):
        rubric_mod.load(path)


def test_file_without_thresholds_raises(tmp_path: Path):
    path = tmp_path / "r.md"
    path.write_text(_MINIMAL.split("## Dimension")[1].join(["## Dimension", ""]))
    with pytest.raises(rubric_mod.RubricParseError, match="no score-threshold"):
        rubric_mod.load(path)


def test_a_minimal_rubric_parses(tmp_path: Path):
    path = tmp_path / "r.md"
    path.write_text(_MINIMAL)
    parsed = rubric_mod.load(path)
    assert len(parsed.dimensions) == 1
    assert parsed.max_total == 5
    assert parsed.verdict(7) == "PASS"
    assert parsed.verdict(2) == "FAIL"
