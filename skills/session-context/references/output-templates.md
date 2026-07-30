# Session Context Output Templates

The briefing the DELIVER phase produces. Executive summary first (< 40 lines), detailed sections
following, every claim cited.

## Executive Summary

```markdown
### Executive Summary

**What changed**: [2-3 sentences summarizing recent activity in/around the focus area. Cite commit
ranges. e.g. "The auth module received 12 commits (abc1234..def5678) over the past week, primarily
adding OAuth 2.0 refresh token support. The payment module had 3 dependency updates (ghi9012..jkl3456)."]

**Key decisions**: [Active ADRs governing this area. e.g. "ADR-0005 (OAuth 2.0 with JWT) governs
authentication. ADR-0012 (PostgreSQL for order service) affects data access patterns."]

**Watch out for**: [Specific warnings. e.g. "auth/token_validator.py changed 7 times this week
(hotspot). ADR-0005 90-day review is 2 weeks overdue."]

**Recommended focus**: [Actionable guidance. e.g. "Review token_validator.py before modifying auth
flows. Check ADR-0005 consequences for token-handling constraints."]
```

## Change Group

```markdown
#### [Group Name: e.g., "OAuth 2.0 Refresh Token Implementation"]

| Commits | Files | Summary |
|---------|-------|---------|
| abc1234..def5678 (Jan 15-20) | 8 | Added refresh token rotation to auth module |

**Key files changed:**
- `src/auth/token_validator.py` -- New refresh token validation logic
- `src/auth/models.py` -- Added RefreshToken model
- `tests/auth/test_refresh.py` -- 12 new tests covering rotation scenarios

**Why this matters for [focus area]:** [One sentence connecting this group to the session focus]
```

## Dependency Context

```markdown
### Dependency Context

**Focus area depends on** (outbound):
- `core.models` -- Stable (unchanged in 3 months), provides base entity types
- `db.session` -- Changed 2x this week (commit abc1234), session management refactored
- `auth.tokens` -- Hotspot (7 changes this week), active feature development

**Depends on focus area** (inbound):
- `api.controllers` -- 4 controllers import from focus area, will need testing if interfaces change
- `workers.background_tasks` -- 2 task handlers reference focus area entities

**Recently changed dependencies** (risk surface):
- `db.session` (commit abc1234, Jan 18): Connection pooling parameters changed. If focus area uses
  long-running transactions, verify timeout behavior.
```

## Hotspot Analysis

```markdown
### File Hotspots

| Rank | File | Changes | Authors | Pattern |
|------|------|---------|---------|---------|
| 1 | src/auth/token_validator.py | 7 | 2 | Active feature development |
| 2 | src/db/session.py | 4 | 1 | Refactoring (high churn) |
| 3 | src/api/middleware.py | 3 | 2 | Bug fixes (3 fix commits) |

**Interpretation:**
- `token_validator.py`: Expect further change. Coordinate with team; consider a review requirement.
- `session.py`: High churn suggests refactoring in progress; may affect any DB-session code.
- `middleware.py`: Three bug fixes suggest fragile code; review recent changes carefully.
```
