---
name: doc-sync
description: Documentation staleness detection, XML doc comment generation, and README synchronization -- keeps documentation accurate and in sync with code changes. Use when auditing documentation coverage, generating XML doc comments, or syncing READMEs after code changes.
---

# Doc Sync

> "The only thing worse than no documentation is wrong documentation. Wrong documentation is not just unhelpful -- it is actively harmful, because someone will trust it and make a bad decision."
> -- Steve McConnell, "Code Complete"

## Core Philosophy

Documentation decays the moment code changes. This skill provides systematic approaches to detect when documentation has drifted from code, generate accurate XML doc comments from implementation analysis, and keep READMEs synchronized with the actual state of the project. The goal is not comprehensive documentation -- it is accurate documentation.

A perfectly documented codebase that was accurate six months ago is a liability today. A minimally documented codebase that was verified this morning is an asset. Freshness and accuracy always beat completeness.

**The Sync Principle:**
Documentation should be treated as a derived artifact of code. When the code changes, the documentation must change. When they diverge, the code is always right.

## Domain Principles

| # | Principle | Rationale | Violation Signal |
|---|-----------|-----------|------------------|
| 1 | **Code Is Truth** | When docs and code disagree, code wins; docs must be updated to match, never the reverse | Docs describe behavior the code does not exhibit; PRs that update docs without checking code |
| 2 | **Detect Before Generating** | Always audit for staleness before writing new docs; you may be duplicating or contradicting existing material | New XML docs added alongside stale existing docs; duplicate documentation of the same API |
| 3 | **Minimal Accurate Over Maximal Stale** | A correct one-line summary beats an incorrect three-paragraph description | Long XML doc comments that describe historical behavior; READMEs with outdated architecture diagrams |
| 4 | **Signature-Driven Documentation** | XML docs should be generated from the actual method signature, not from assumptions about intent | Param docs that do not match parameter names; return docs for void methods; missing exception docs |
| 5 | **Staleness Has a Half-Life** | Documentation accuracy decays exponentially with time since last verification; prioritize recently changed code | Six-month-old docs on actively developed code treated as current; no git blame comparison |
| 6 | **README Is the Front Door** | READMEs are read first and most often; they must reflect the current project state or they mislead every new reader | Setup instructions that reference removed dependencies; feature lists that omit major capabilities |
| 7 | **Document the Why, Not the What** | The code shows what happens; docs should explain why it matters, what constraints apply, and what callers need to know | XML summaries that restate the method name; "Gets the value" on a GetValue method |
| 8 | **Exceptions Are Contract** | Exception documentation is part of the public API contract; undocumented exceptions are bugs in your documentation | Methods that throw without doc; catch blocks that handle undocumented exception types |
| 9 | **Examples Must Compile** | Code examples in documentation that do not compile teach the wrong thing | Pseudocode in example tags; examples referencing renamed classes; examples with wrong parameter counts |
| 10 | **Cross-Reference Aggressively** | Related types and methods should link to each other; isolated docs force readers to search | See-also tags missing; related classes not cross-referenced; overloads not linking to each other |

## Workflow

### Staleness Detection

```
SCAN
    Identify documentation scope:
    - Target directory or namespace
    - File types to consider (.cs, .md, .xml)
    - Documentation types to check (XML comments, README, API docs)

        |
        v

COMPARE
    For each code file with documentation:
    - Get last modification date of code (git log)
    - Get last modification date of corresponding doc
    - Compare API signatures against doc content
    - Check for new public members without docs
    - Check for removed members still in docs

        |
        v

CLASSIFY
    Categorize each documentation item:
    - CURRENT: Doc matches code, recently verified
    - STALE: Code changed after doc was last updated
    - MISSING: Public API with no documentation
    - ORPHANED: Doc references code that no longer exists
    - DRIFT: Doc exists but does not match current signatures

        |
        v

PRIORITIZE
    Order items for update:
    1. ORPHANED (actively misleading)
    2. DRIFT (incorrect information)
    3. STALE (probably incorrect)
    4. MISSING on public APIs (gaps in coverage)
    5. CURRENT (verify and move on)
```

### XML Doc Comment Generation

```
READ
    Before writing any XML doc:
    1. Read the full method/property/type implementation
    2. Note the exact signature (parameters, return type, generic constraints)
    3. Identify all code paths that throw exceptions
    4. Identify edge cases and boundary conditions
    5. Check for existing XML docs that may need updating

        |
        v

GENERATE
    Write XML doc comments following these rules:
    - <summary> describes WHAT and WHY, not HOW
    - <param> for every parameter, describing constraints and valid ranges
    - <returns> for every non-void return, describing all possible outcomes
    - <exception> for every thrown exception, describing the condition
    - <remarks> for edge cases, threading concerns, performance notes
    - <example> only when the usage is non-obvious
    - <see cref="..."/> for related types and members

        |
        v

VERIFY
    Validate the generated docs:
    - Every <param name="X"> matches an actual parameter named X
    - Every <exception cref="T"> matches an exception actually thrown
    - Every <see cref="M"/> references an existing member
    - <returns> is absent for void methods
    - <example> code is syntactically valid
    - Summary does not merely restate the member name
```

### README Synchronization

```
INVENTORY
    Determine what the README covers:
    - Project description and purpose
    - Installation / setup instructions
    - Configuration options
    - Usage examples
    - API overview or quick reference
    - Contributing guidelines
    - Dependency list

        |
        v

DIFF
    Compare each README section against current state:
    - Do setup instructions match current build files?
    - Do dependency lists match current package manifests?
    - Do usage examples reference current API signatures?
    - Does the project description match current capabilities?
    - Are configuration options still valid?

        |
        v

UPDATE
    For each stale section:
    1. Read the current code/config that the section describes
    2. Update the section to match reality
    3. Preserve the existing writing style and format
    4. Do not add new sections unless there is an obvious gap
    5. Mark sections you cannot verify with a note

        |
        v

VALIDATE
    Confirm the updated README:
    - All file paths reference existing files
    - All command examples are valid
    - All dependency versions match manifests
    - All API references match current signatures
    - Section order and formatting is preserved
```

## State Block

Track the current doc-sync operation:

```markdown
<doc-sync-state>
phase: SCAN | COMPARE | CLASSIFY | GENERATE | VALIDATE
scope: [directory, namespace, or file]
files_scanned: [count]
gaps_found: [count]
stale_docs: [count]
items_updated: [count]
items_validated: [count]
last_verified: [description of last action]
</doc-sync-state>
```

## Output Templates

### Staleness Report Template

```markdown
# Documentation Staleness Report

**Scope**: [directory/namespace]
**Date**: [YYYY-MM-DD]
**Files analyzed**: [count]

## Summary

| Category | Count | Action Required |
|----------|-------|-----------------|
| Current | [N] | None |
| Stale | [N] | Update docs |
| Missing | [N] | Generate docs |
| Orphaned | [N] | Remove docs |
| Drift | [N] | Correct docs |

## Critical Items (Orphaned + Drift)

| File | Member | Issue | Last Code Change | Last Doc Change |
|------|--------|-------|------------------|-----------------|
| [path] | [member] | [category] | [date] | [date] |

## Stale Items

| File | Member | Days Since Code Change | Days Since Doc Change |
|------|--------|----------------------|---------------------|
| [path] | [member] | [N] | [N] |

## Missing Documentation

| File | Member | Visibility | Priority |
|------|--------|-----------|----------|
| [path] | [member] | public | [high/medium/low] |
```

### XML Doc Coverage Report Template

```markdown
# XML Doc Coverage: [Namespace/Project]

**Date**: [YYYY-MM-DD]
**Total public members**: [count]
**Documented**: [count] ([percentage]%)
**Missing docs**: [count]

## Coverage by Type

| Type | Total Members | Documented | Missing | Coverage |
|------|--------------|------------|---------|----------|
| [ClassName] | [N] | [N] | [N] | [%] |

## Missing Documentation Details

### [ClassName]

- `MethodName(ParamType)` -- public, no XML doc
- `PropertyName` -- public, no XML doc

## Quality Issues

| File | Member | Issue |
|------|--------|-------|
| [path] | [member] | Summary restates method name |
| [path] | [member] | Missing exception documentation |
| [path] | [member] | Param name mismatch |
```

## AI Discipline Rules

### CRITICAL: Read Before Writing

ALWAYS read the full implementation of any code member before generating documentation for it. Never generate XML doc comments from the method signature alone -- the signature tells you the types, but the implementation tells you the behavior, the edge cases, and the exceptions. A doc comment generated without reading the implementation is a guess, and guesses become lies.

### CRITICAL: Verify Every Reference

EVERY `<see cref="..."/>`, `<paramref name="..."/>`, and `<typeparamref name="..."/>` must be verified against actual code. A broken cref in an XML doc comment is not just a warning -- it is a broken link in generated API documentation that will confuse every reader. Before writing a cross-reference, confirm the target exists. After writing it, verify it resolves.

### CRITICAL: Do Not Hallucinate APIs

If you cannot find a method, property, or type in the codebase, it does not exist and must not be documented. This is the single most dangerous failure mode for AI-generated documentation. Before documenting any member, use Grep or Glob to confirm it exists. If you are uncertain whether something is public or internal, check the access modifier. When in doubt, leave it out.

### CRITICAL: Preserve Voice and Convention

Every project has a documentation voice. Some use formal third person ("Gets the configuration value"). Some use imperative ("Get the configuration value"). Some use casual language. Before writing new documentation, read existing documentation in the same project and match the style exactly. Inconsistent documentation voice signals carelessness and erodes trust.

### CRITICAL: Staleness Is the Default State

Assume all documentation is stale until proven otherwise. When you encounter documentation, your first instinct should be to verify it, not trust it. Check the git history. Compare signatures. Read the implementation. Documentation that was correct when written may be wrong today. Treat verification as the primary task and writing as secondary.

## Anti-Patterns

### The Parrot Summary

**What it looks like**: `/// <summary>Gets the user.</summary>` on a method named `GetUser()`. The doc comment adds zero information beyond what the method name already communicates.

**Why it is harmful**: Developers learn to ignore XML doc comments because they contain no useful information. When a comment finally does say something meaningful, it gets skipped because the reader has been trained that comments are noise.

**How to address**: Summaries should answer "why would I call this?" and "what should I know before calling it?" For example: "Retrieves the user by ID from the cache, falling back to the database if not found. Returns null if the user does not exist."

### The Stale README

**What it looks like**: A README that references `dotnet 6.0` when the project has migrated to `dotnet 8.0`. Setup instructions that mention packages no longer in the dependency list. Architecture diagrams showing components that were removed two quarters ago.

**Why it is harmful**: Every new team member follows these instructions, wastes time, and loses trust in all project documentation. The README is the most-read document in any repository -- when it is wrong, the damage is amplified.

**How to address**: Run README sync after every significant change. Compare dependency lists against manifests. Compare setup instructions against the actual build process. Treat the README as code that must be kept in sync.

### The Missing Exception Doc

**What it looks like**: A method that throws `ArgumentNullException`, `InvalidOperationException`, and `HttpRequestException`, but the XML docs only mention the return value. Callers discover the exceptions at runtime.

**Why it is harmful**: Exception documentation is part of the API contract. When callers do not know what exceptions a method can throw, they either catch too broadly (hiding bugs) or too narrowly (crashing in production). Missing exception docs are a documentation bug with production consequences.

**How to address**: For every method, trace all code paths that throw. Include `<exception cref="T">` for each one, describing the condition that triggers it. Check catch blocks in callers to verify they handle documented exceptions.

## Error Recovery

### Git History Unavailable

**Symptoms**: Cannot compare doc dates against code dates because git history is shallow or missing.

**Recovery protocol**:
1. Fall back to file modification timestamps (less reliable but available).
2. If timestamps are unreliable, do a full signature comparison instead.
3. Compare every XML doc param/return against the actual code signature.
4. Flag the session as "timestamp-unavailable" in the staleness report.
5. Recommend the team configure full git history for documentation audits.

### Ambiguous Code Behavior

**Symptoms**: Cannot determine what a method does from reading the implementation -- logic is convoluted, side effects are hidden, or behavior depends on runtime state.

**Recovery protocol**:
1. Document what you can verify (signature, parameter types, return type).
2. Add a `<remarks>` noting that behavior analysis was inconclusive.
3. Flag the item for human review with a TODO comment.
4. Do not guess. An incomplete doc with a TODO is better than a confident wrong doc.
5. Check if tests exist that clarify the expected behavior.

### Conflicting Doc Sources

**Symptoms**: XML comments say one thing, README says another, wiki says a third.

**Recovery protocol**:
1. Read the actual implementation -- code is the source of truth.
2. Update XML comments first (closest to the code).
3. Update README next (most visible to readers).
4. Flag other sources (wiki, external docs) for manual update.
5. Log which sources were in conflict in the session report.

## Integration

This skill works with and references the following related skills:

- **architecture-journal** -- When documentation audits reveal significant architecture decisions that are undocumented, use architecture-journal to record them as ADRs. Documentation gaps often indicate decision gaps.

**Workflow integration example**:
1. Use doc-sync to audit documentation coverage
2. Discover that a major API redesign was never documented
3. Use architecture-journal to record the redesign decision as an ADR
4. Return to doc-sync to update XML docs and README for the new API

## Stack-Specific Guidance

See reference files for detailed patterns and heuristics:

- [XML Doc Patterns](references/xml-doc-patterns.md) -- C# XML documentation tag patterns, when to use each tag, common anti-patterns, and quality examples
- [Staleness Detection](references/staleness-detection.md) -- Heuristics for detecting stale documentation using git blame comparison, API signature drift, missing type coverage, and broken code examples
