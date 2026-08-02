# <AI-Generated START>
"""Filling in ``evals.md``'s Last Run / Result fields from real output.

Every one of those fields has been empty since the file was written, which is the whole
problem: a test case with no recorded run is a claim, not a result. This rewrites only
those two fields, in place, line-scoped and idempotent — it never reformats the document
or touches the criteria, because the criteria are the human's.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_TEST_CASE = re.compile(r"^###\s+Test Case\s+(\d+)\s*[—:-]?\s*(.*)$")
_LAST_RUN_LINE = re.compile(r"^(\s*[-*]\s*\*\*Last Run:\*\*).*$")
_RESULT_LINE = re.compile(r"^(\s*[-*]\s*\*\*Result:\*\*).*$")
_COMBINED = re.compile(r"^(\s*[-*]\s*\*\*Last Run:\*\*)\s*(.*?)\s*\|\s*(\*\*Result:\*\*)\s*(.*)$")


@dataclass(frozen=True)
class RunRecord:
    """What actually happened, for one test case."""

    test_case: int
    date: str
    command: str
    result: str

    @property
    def last_run(self) -> str:
        return f"{self.date} (`{self.command}`)"


def update(text: str, records) -> str:
    """Return ``text`` with the Last Run / Result fields of the named test cases filled."""
    by_case = {r.test_case: r for r in records}
    lines = text.splitlines()
    current: int | None = None
    out: list[str] = []

    for line in lines:
        header = _TEST_CASE.match(line)
        if header:
            current = int(header.group(1))
            out.append(line)
            continue

        record = by_case.get(current) if current is not None else None
        if record is None:
            out.append(line)
            continue

        combined = _COMBINED.match(line)
        if combined:
            out.append(
                f"{combined.group(1)} {record.last_run} | {combined.group(3)} {record.result}"
            )
            continue
        last_run = _LAST_RUN_LINE.match(line)
        if last_run:
            out.append(f"{last_run.group(1)} {record.last_run}")
            continue
        result = _RESULT_LINE.match(line)
        if result:
            out.append(f"{result.group(1)} {record.result}")
            continue
        out.append(line)

    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def update_file(path: str | Path, records) -> bool:
    """Rewrite ``path`` in place. Returns True if anything changed."""
    path = Path(path)
    before = path.read_text()
    after = update(before, records)
    if after == before:
        return False
    path.write_text(after)
    return True


def record_from_lint(findings, date: str, total_skills: int = 0) -> RunRecord:
    n_err, n_warn = len(findings.errors), len(findings.warnings)
    verdict = "PASS" if not n_err else "FAIL"
    scope = f" over {total_skills} skills" if total_skills else ""
    return RunRecord(
        test_case=1,
        date=date,
        command="skill-evals lint",
        result=f"{verdict} — {n_err} error(s), {n_warn} warning(s){scope}",
    )


def record_from_routing(result, date: str, test_case: int = 10) -> RunRecord:
    s = result.summary
    verdict = "PASS" if not result.breaches else "FAIL"
    return RunRecord(
        test_case=test_case,
        date=date,
        command="skill-evals route",
        result=(
            f"{verdict} — top-1 {s.accuracy:.2f} over {s.total} cases, "
            f"{len(result.collisions)} collision(s), {s.parse_failures} parse failure(s)"
        ),
    )


def record_from_scorecard(result, date: str, test_case: int = 9) -> RunRecord:
    verdicts = result.summary["verdicts"]
    parts = ", ".join(f"{n} {v}" for v, n in sorted(verdicts.items()))
    verdict = "PASS" if not result.deprecate else "FAIL"
    return RunRecord(
        test_case=test_case,
        date=date,
        command="skill-evals scorecard",
        result=(
            f"{verdict} — mean {result.summary['mean_total']:.1f}/"
            f"{result.summary['max_total']} ({parts})"
        ),
    )
# <AI-Generated END>
