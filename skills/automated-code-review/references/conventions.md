# Automated Review Conventions

Depth behind the Core Philosophy: the principle set, knowledge-base grounding, phase gates, the
finding pipeline, and the minimum per-category checklists. Detailed sub-item guidance lives in
`review-checklist-engine.md`; convention-detection procedures in `convention-detection.md`.

## Domain Principles

| # | Principle | Description | Enforcement |
|---|-----------|-------------|-------------|
| 1 | **Checklist as Floor** | The checklist defines the minimum review scope. The agent can find issues beyond it, but cannot skip checklist items. A review that misses a checklist item is incomplete regardless of what else it found. | HARD — every checklist item marked pass/fail/N-A |
| 2 | **Convention Before Judgment** | Before reporting any style or convention finding, detect the project's actual conventions. Reporting against external standards when the project differs is a false positive. | HARD — convention detection gates the ANALYZE phase |
| 3 | **Evidence for Every Finding** | Every finding includes the specific code (line numbers, snippet) that triggers it. "Poor error handling" is not a finding; "Line 42: `except Exception: pass` swallows all exceptions" is. | HARD — findings without evidence are rejected |
| 4 | **Severity from Impact** | Severity is the impact in the project's actual context, not the theoretical worst case. A SQL injection in an internal tool with no user input is lower severity than the same pattern in a public API. | HARD — severity must include context reasoning |
| 5 | **False Positive Prevention** | Before reporting, verify against framework behavior, middleware, project patterns, and surrounding code. Aim for a lower false-positive rate than a hurried human, not higher. | HARD — false-positive check is part of every finding |
| 6 | **Structured Output** | Output follows a consistent format across reviews so consumers (human or CI) parse it predictably. Ad hoc formatting is not acceptable. | HARD — output matches defined templates |
| 7 | **Category Completeness** | All five categories (security, correctness, performance, maintainability, style) are evaluated for every file in scope. "Looks fine" is not permitted — run the checklist explicitly. | HARD — per-category results logged for every file |
| 8 | **Incremental Context** | When reviewing a diff, read the full file. A diff-only review misses issues from interactions between changed and unchanged code. | MEDIUM — full file context required for diff reviews |
| 9 | **Convention Drift Detection** | When a file's conventions differ from the project's, distinguish "this file is wrong" from "this file predates the convention." Old working code is not necessarily a finding. | MEDIUM — flag convention age when reporting style findings |
| 10 | **Positive Signal** | Report what the code does well, not just what is poor. At minimum, one positive observation per file reviewed. | MEDIUM — positive observations section required in output |

## Knowledge Base Lookups

Use `search_knowledge` (grounded-code-mcp) to ground decisions. Search at the start of SCAN to
calibrate checklists, and during ANALYZE when an item needs deeper verification. Cite the source in
findings where authoritative guidance informed severity.

| Query | When to Call |
|-------|--------------|
| `search_knowledge("OWASP top 10 injection SQL XSS")` | SCAN — calibrate security checklist to current OWASP guidance |
| `search_knowledge("code review correctness error handling")` | ANALYZE — verify correctness checklist completeness |
| `search_knowledge("N+1 query performance database loop")` | ANALYZE — confirm performance patterns |
| `search_knowledge("cyclomatic complexity maintainability code smell")` | ANALYZE — ground maintainability thresholds |
| `search_knowledge("clean code naming conventions single responsibility")` | Convention detection — calibrate naming/responsibility |
| `search_knowledge("security authentication authorization access control")` | Security checklist — verify auth/authz patterns |

## Phase Gates

The review cannot advance to the next phase without passing the current phase's exit gate.

**SCAN exit gate** — all true:
- [ ] Review scope explicitly defined (diff, files, directory, PR)
- [ ] All files in scope enumerated with languages identified
- [ ] Project conventions detected (or explicitly marked "unable to detect")
- [ ] Tech stack and frameworks identified
- [ ] At least 3 existing project files sampled for convention detection

**ANALYZE exit gate** — all true for every file in scope:
- [ ] File read completely (not partially, not from cache)
- [ ] Security / Correctness / Performance / Maintainability checklists run — all items pass/fail/N-A
- [ ] Style checklist run against detected conventions — all items pass/fail/N-A
- [ ] Every finding has evidence (line number + snippet), category, and severity
- [ ] False-positive check completed for every finding

**SYNTHESIZE exit gate** — all true:
- [ ] Duplicate findings merged; cross-file issues identified
- [ ] Findings ranked by severity; related findings grouped into themes
- [ ] Final false-positive review completed on the consolidated list

**REPORT exit gate** — all true:
- [ ] Output follows the structured template (see `output-templates.md`)
- [ ] Every finding has evidence, category, severity, and suggested fix
- [ ] Findings ordered by severity (critical first); positive observations included
- [ ] "Needs verification" findings flagged separately; review statistics computed

## Finding Pipeline

Every potential finding passes through this pipeline before inclusion:

```
DETECT → VERIFY → CATEGORIZE → SEVERITY → FORMAT → INCLUDE

1. DETECT      Agent notices a potential issue
2. VERIFY      Is this actually an issue? Reachable in execution? Handled by framework/middleware?
               Intentional project pattern? If not verified → DISCARD (log as filtered false positive)
3. CATEGORIZE  Assign primary category (security/correctness/performance/maintainability/style)
4. SEVERITY    Assign by impact in context — who is affected, how often, blast radius.
               If ambiguous → mark "needs verification"
5. FORMAT      Produce structured finding with evidence
6. INCLUDE     Add to findings list
```

## Minimum Checklists (the floor)

Detailed sub-items, automated pass/fail criteria, and language extensions are in
`review-checklist-engine.md`. The minimum every review must run:

**Security:** inputs traced to terminal use · SQL/NoSQL injection (parameterized?) · auth/authz on
every controlled path · sensitive data not in logs/errors/responses · crypto algorithms + key
management · path traversal · untrusted deserialization · dependency vulnerabilities (if manifest).

**Correctness:** boundary cases on conditionals · off-by-one + loop termination · null/nil/undefined
at every dereference · error handling for every fallible operation · error paths don't swallow
silently · type consistency · concurrency primitives correct · resource cleanup in all paths.

**Performance:** no O(n²)+ on unbounded/user-controlled input · no queries in loops (N+1) · no
blocking I/O in async contexts · no unbounded collection growth · pagination/streaming for large
sets · no needlessly repeated expensive operations.

**Maintainability:** single clear responsibility · no uncontextualized magic values · descriptive
consistent naming · no copy-paste duplication (Rule of Three) · abstraction levels not mixed · error
messages carry diagnostic context · no dead code.

**Style (against detected conventions):** naming · formatting (indent/braces/line length) · import
organization · language idioms · file organization · no unused imports/variables.
