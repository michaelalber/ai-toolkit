# Executive Summary Template — PHP Security Review

The executive summary is for a non-technical decision-maker. Lead with risk and business impact,
not vulnerability names. Translate every finding into "what could happen" and "what it costs to fix".

---

## Template

```markdown
## Security Review — [Application] (PHP / Laravel)
**Date**: [date] · **Scope**: [paths / modules] · **Overall risk grade**: [A–F]

### Bottom line
[2–3 plain sentences: is this safe to ship? What is the single most serious risk, in business terms?]

### Findings at a glance
| Severity | Count | Meaning |
|----------|-------|---------|
| Critical | [N] | Exploitable now; could expose data or allow account takeover |
| High | [N] | Serious; exploitable under realistic conditions |
| Medium | [N] | Should fix; limited impact or requires unusual conditions |
| Low | [N] | Hardening / defense-in-depth |

### Top 3 risks (plain language)
1. **[Risk]** — [what an attacker could do] — [effort to fix: S/M/L]
2. **[Risk]** — …
3. **[Risk]** — …

### Recommendation
[Ship / ship-with-fixes / do-not-ship], and the smallest set of changes that changes that answer.
```

---

## Translation guide (vuln → business language)

| Finding | Say instead |
|---------|-------------|
| SQL injection via `whereRaw` | "An attacker could read or modify the entire database through the search box." |
| Mass-assignment unguarded | "A user could grant themselves admin rights by adding a field to a form submission." |
| `APP_DEBUG=true` in prod | "Error pages expose database credentials and file paths to anyone who triggers an error." |
| Object injection via `unserialize` | "A crafted cookie could run attacker code on the server." |
| Secrets in code/logs | "API keys are visible to anyone with read access to the repo or logs." |

Keep the summary to one screen. The technical findings table carries the `file:line` detail.
