# Executive Summary Template — React Security Review

The executive summary is for a non-technical decision-maker. Lead with risk and business impact,
not vulnerability names. Translate every finding into "what could happen" and "what it costs to fix".

---

## Template

```markdown
## Security Review — [Application] (React / front-end)
**Date**: [date] · **Scope**: [paths / routes] · **Overall risk grade**: [A–F]

### Bottom line
[2–3 plain sentences: is this safe to ship? What is the single most serious risk, in business terms?]

### Findings at a glance
| Severity | Count | Meaning |
|----------|-------|---------|
| Critical | [N] | Exploitable now; could run code in users' browsers or steal their sessions |
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
| XSS via unsanitized raw HTML | "An attacker could run code in any user's browser — stealing their logged-in session or keystrokes." |
| Token in `localStorage` | "If any script flaw exists, the attacker can read the login token and impersonate the user." |
| API key shipped in the bundle | "The secret is downloadable by anyone who visits the site — it must be treated as already leaked." |
| Client-only authorization | "Hiding the admin button doesn't stop anyone; the server must reject the request, and today it may not." |
| Open redirect via `?next=` | "A phishing link on your domain could bounce users to an attacker's site that looks trusted." |
| Vulnerable dependency (CVE) | "A third-party package has a known, published flaw; updating it closes a publicly-documented hole." |

Remember: in a front-end review, **the most expensive finding is usually a *missing* server-side check**
that the UI was quietly relying on. Name it as a backend fix even though you found it in the client.

Keep the summary to one screen. The technical findings table carries the `file:line` detail.
