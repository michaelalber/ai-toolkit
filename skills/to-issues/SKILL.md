---
name: to-issues
description: >
  Converts a PRD or feature spec into a set of atomic GitHub Issues ready to open,
  each covering one independently-deliverable slice ordered by dependency. Use when
  asked to "create issues", "break this into GitHub issues", "turn this PRD into issues",
  or "decompose this feature into tickets".
  Ported from https://github.com/mattpocock/skills (Matt Pocock).
---

Convert the PRD or feature description into GitHub Issues.

## Rules

- Each issue = one independently-deliverable, testable slice
- Order issues by dependency: infrastructure → data model → API → UI → polish
- No issue should take more than 2 days; split if larger
- Every issue has: title, type, description, acceptance criteria, and dependency notes

See `references/decomposition-patterns.md` for how to slice a feature.

## Instructions

1. Read the PRD/spec completely.
2. Identify natural decomposition seams — by feature, layer, risk, or team boundary.
3. Write issues in dependency order — note blocking relationships explicitly.
4. Use the format in `references/issue-template.md` for each issue.
5. Present the full list: "Does this order make sense? Any issues missing?"
6. If confirmed, offer to open with `gh issue create` one by one.
