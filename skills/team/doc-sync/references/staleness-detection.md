# Staleness Detection Reference

## Overview

Documentation becomes stale the moment the code it describes changes. This reference provides concrete heuristics for detecting when documentation has drifted from the code, how to measure the severity of that drift, and how to prioritize what to fix first. These heuristics are designed to be applied programmatically using git history, file comparison, and signature analysis.

## Heuristic 1: Git Blame Comparison

The most reliable indicator of staleness is comparing when the code last changed versus when its documentation last changed.

### Method

```
For each documented code member:
1. Get the last commit date that modified the code implementation
2. Get the last commit date that modified the corresponding documentation
3. If code_date > doc_date, the documentation is potentially stale
4. Calculate the drift: days between code change and doc change
```

### Git Commands

```bash
# Last modification date of a specific file
git log -1 --format="%ai" -- src/Services/UserService.cs

# Last modification date of a specific line range (method body)
git log -1 --format="%ai" -L 45,80:src/Services/UserService.cs

# Compare code file vs doc file modification dates
CODE_DATE=$(git log -1 --format="%ai" -- src/Services/UserService.cs)
DOC_DATE=$(git log -1 --format="%ai" -- docs/api/UserService.md)

# Files changed since a documentation file was last updated
DOC_COMMIT=$(git log -1 --format="%H" -- docs/api/UserService.md)
git diff --name-only $DOC_COMMIT..HEAD -- src/Services/
```

### Severity Classification

| Drift (days) | Severity | Action |
|--------------|----------|--------|
| 0-7 | Low | Likely still current; verify if commit was substantive |
| 8-30 | Medium | Review for accuracy; signature changes are likely |
| 31-90 | High | Assume stale; full re-read of code required before trusting |
| 91+ | Critical | Treat as missing; rewrite from scratch by reading current code |

### Edge Cases

- **Formatting-only commits**: A code file reformatted (whitespace changes, using directive sorting) will show as modified, but the docs are not stale. Check the diff content, not just the date.
- **Doc-only commits**: If docs were updated more recently than code, they may be current. But verify -- the doc update might have been for a different member in the same file.
- **Bulk renames**: Namespace or file renames change git dates for every file. Compare the actual content, not just timestamps.

## Heuristic 2: API Signature Drift

When method signatures change but documentation does not update, the docs become actively misleading.

### What to Compare

```
For each documented public member, compare:

METHOD SIGNATURES:
- Method name (renamed?)
- Parameter count (added or removed?)
- Parameter names (renamed?)
- Parameter types (changed?)
- Return type (changed?)
- Generic constraints (added, removed, or changed?)
- Access modifier (public -> internal?)

PROPERTY SIGNATURES:
- Property name (renamed?)
- Property type (changed?)
- Getter/setter presence (added or removed setter?)
- Access modifier changes

CLASS/INTERFACE SIGNATURES:
- Type name (renamed?)
- Base class (changed?)
- Implemented interfaces (added or removed?)
- Generic parameters (changed?)
```

### Detection Patterns

```
PARAMETER MISMATCH:
  Doc says: <param name="userId">
  Code has: public void DoThing(int accountId)
  Result:   DRIFT -- parameter was renamed

RETURN TYPE MISMATCH:
  Doc says: <returns>The user profile</returns>
  Code has: public void DeleteUser(int userId)
  Result:   DRIFT -- method was changed to void, docs still describe return

MISSING PARAMETER:
  Doc says: <param name="userId"> and <param name="name">
  Code has: public void Update(int userId, string name, string email)
  Result:   INCOMPLETE -- new parameter "email" has no documentation

EXTRA PARAMETER DOC:
  Doc says: <param name="userId">, <param name="name">, <param name="email">
  Code has: public void Update(int userId, string name)
  Result:   ORPHANED -- "email" parameter was removed, doc remains
```

### Automated Comparison Approach

```
1. Parse XML doc comments to extract documented parameter names
2. Parse method signature to extract actual parameter names
3. Compare the two sets:
   - In docs but not in code -> ORPHANED doc (remove)
   - In code but not in docs -> MISSING doc (add)
   - In both but names differ -> DRIFT (update)
4. Compare return type:
   - Doc describes return but method is void -> DRIFT
   - Method returns value but no <returns> tag -> MISSING
5. Compare exception docs:
   - Doc lists exception but code does not throw it -> ORPHANED
   - Code throws exception but doc does not list it -> MISSING
```

## Heuristic 3: Missing New Types and Members

When new public types or members are added without documentation, coverage decreases silently.

### Detection Method

```
1. Scan all source files in scope for public/protected declarations
2. Build a list of all public types and members
3. Check each against existing documentation:
   - XML doc comment present in source? (for inline docs)
   - Entry in API documentation file? (for external docs)
   - Mentioned in README? (for high-level types)
4. Flag any undocumented public member as MISSING

PRIORITY ORDER:
  1. Public types with no summary at all
  2. Public methods with no parameter documentation
  3. Public methods with no exception documentation
  4. Public properties with no summary
  5. Protected members (lower priority but still needed)
```

### Scanning Patterns by Language

**C# public member detection**:
```
Look for these patterns in source files:
- public class/struct/interface/record/enum declarations
- public/protected method declarations
- public/protected property declarations
- public/protected event declarations
- public constructor declarations

Exclude:
- Internal, private, and file-scoped types
- Compiler-generated members (auto-properties backing fields)
- Override methods (doc is inherited from base)
- Explicit interface implementations (doc is on the interface)
```

**README coverage check**:
```
For each top-level public type:
- Is it mentioned in the README's API overview section?
- Is its primary use case described?
- Are there examples showing how to use it?

For new types added since the README was last updated:
- Flag as MISSING from README
- Prioritize types that are part of the public API surface
```

### Tracking New Additions Over Time

```bash
# Find public types added since a specific date or commit
git log --since="2024-01-01" --diff-filter=A --name-only -- "*.cs" | sort -u

# Find files modified but not in the docs directory
git log --since="2024-01-01" --name-only -- "src/" | sort -u | \
  while read f; do
    basename="${f%.cs}"
    if ! grep -q "$basename" docs/api/*.md 2>/dev/null; then
      echo "UNDOCUMENTED: $f"
    fi
  done

# Count public members per file (rough heuristic)
grep -c "public " src/Services/UserService.cs
```

## Heuristic 4: Broken Code Examples

Code examples in documentation that no longer compile or reference removed APIs are actively harmful.

### What to Check

```
For each code example in documentation:

1. SYNTAX VALIDITY
   - Does the example use valid language syntax?
   - Are all types referenced actually available?
   - Are all methods called with the correct number/type of arguments?

2. API REFERENCE VALIDITY
   - Do class names in examples match current class names?
   - Do method names in examples match current method names?
   - Do constructor signatures in examples match current constructors?
   - Do namespace imports in examples reference existing namespaces?

3. BEHAVIORAL ACCURACY
   - Does the example demonstrate current behavior?
   - Are default values in examples still the actual defaults?
   - Are return types in examples still correct?
   - Do exception handling patterns match current exception types?
```

### Common Breakage Patterns

| Breakage Type | Example | Detection Method |
|---------------|---------|------------------|
| Renamed class | Example uses `UserManager`, code has `UserService` | Grep example class names against codebase |
| Removed method | Example calls `GetById()`, method was removed | Grep example method calls against codebase |
| Changed signature | Example passes 2 args, method now takes 3 | Compare example call sites against method signatures |
| Changed namespace | Example imports `Company.Users`, now `Company.Identity` | Compare using statements against actual namespaces |
| Changed return type | Example assigns to `User`, method now returns `UserDto` | Compare variable types in examples against return types |
| Removed overload | Example uses `Create(name)`, only `Create(name, email)` exists | Check that the specific overload called still exists |
| Changed defaults | Example relies on default `timeout=30`, now `timeout=60` | Compare documented defaults against code defaults |

### Automated Example Validation

```
For each <example> or ```csharp block in documentation:

1. Extract all type references (class names, interface names)
2. Verify each exists in the codebase using grep/glob
3. Extract all method calls
4. Verify each method exists on the referenced type
5. Extract constructor calls
6. Verify constructor signatures match

Flag as BROKEN if any reference does not resolve.
Flag as SUSPECT if the example file was last updated 90+ days ago.
```

## Priority Matrix

When multiple staleness issues are found, prioritize in this order:

| Priority | Category | Rationale |
|----------|----------|-----------|
| 1 | Broken examples | Actively teaches wrong patterns to developers |
| 2 | Orphaned docs (removed APIs) | Misleads developers into using nonexistent APIs |
| 3 | Signature drift | Incorrect parameter/return docs cause runtime errors |
| 4 | Missing exception docs | Callers cannot write correct error handling |
| 5 | Stale README sections | New team members get wrong setup/usage info |
| 6 | Missing docs on new types | Coverage gap but not actively misleading |
| 7 | Missing docs on new members | Lower coverage but type-level docs may suffice |
| 8 | Style inconsistencies | Cosmetic but erodes trust over time |

## Staleness Score

Calculate a numeric staleness score for prioritization:

```
BASE SCORE = days_since_code_change - days_since_doc_change

MULTIPLIERS:
  x3.0 if signature has changed (parameters, return type)
  x2.5 if examples reference removed APIs
  x2.0 if new public members have been added without docs
  x1.5 if the member is part of a public NuGet package API
  x1.0 if the member is internal-facing only

FINAL SCORE = BASE_SCORE * highest_applicable_multiplier

THRESHOLDS:
  Score 0-50:    LOW -- schedule for next documentation pass
  Score 51-150:  MEDIUM -- address within the current sprint
  Score 151-300: HIGH -- address this week
  Score 301+:    CRITICAL -- address immediately, docs are harmful
```

## Integration with CI/CD

### Suggested Checks

```
PRE-MERGE CHECK:
  For each file in the PR diff:
  1. If a public method signature changed, verify XML docs updated
  2. If a new public type was added, verify XML docs exist
  3. If a dependency version changed, verify README mentions current version
  4. If a code example file changed, verify doc examples still reference it

POST-MERGE REPORT:
  Weekly or per-release:
  1. Run full staleness scan across the project
  2. Generate coverage report (% of public members documented)
  3. Generate drift report (docs older than their code)
  4. Track trends: is documentation coverage improving or declining?
```

### Threshold Recommendations

```
MINIMUM VIABLE DOCUMENTATION:
  - 100% of public types have <summary>
  - 100% of public method parameters have <param>
  - 100% of thrown exceptions have <exception>
  - 0 orphaned documentation entries
  - 0 broken code examples

GOOD DOCUMENTATION:
  - All of the above, plus:
  - 100% of non-void methods have <returns>
  - All types with non-obvious usage have <example>
  - README is verified current within 30 days
  - All cross-references resolve

EXCELLENT DOCUMENTATION:
  - All of the above, plus:
  - <remarks> on all complex members
  - Cross-references between related types
  - README includes architecture overview
  - Staleness score below 50 for all members
```
