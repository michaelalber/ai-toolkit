# Orientation Checklist — Large Codebase Edition

Use this checklist when zooming out on a large or unfamiliar codebase where the basic
zoom-out map isn't enough.

## Layer 1: Current location

- [ ] What file am I in? What is its stated purpose (comment, name, README)?
- [ ] What function/class/module am I in?
- [ ] What is this code's single responsibility?
- [ ] What are its direct inputs and outputs?

## Layer 2: Immediate callers

- [ ] Who calls this function/uses this class?
- [ ] How many call sites exist? (grep/LSP)
- [ ] Are all call sites passing the same arguments, or do some differ?
- [ ] Is this code called on the critical path (request handling, startup) or off-path?

## Layer 3: Module boundary

- [ ] What does this module export to the outside world?
- [ ] What does it keep internal?
- [ ] What would break if I changed its public interface?
- [ ] Is there a clear owner/team for this module?

## Layer 4: Domain role

- [ ] What user-facing feature does this code enable?
- [ ] What bounded context (if DDD is used) does it belong to?
- [ ] What domain concept does the key data type represent?

## Layer 5: Non-obvious constraints

- [ ] Are there performance constraints? (comments, benchmarks, profiling annotations)
- [ ] Are there concurrency constraints? (locks, channels, async boundaries)
- [ ] Are there security constraints? (auth, validation, logging exclusions)
- [ ] Are there external system contracts? (API versioning, message format)

## Report format

```
Current location: path/to/file.ext:N — FunctionName — one-line purpose
Callers: [file:line — context], [file:line — context]
Module exports: [list of public API surface]
Domain role: [feature / bounded context / concept]
Constraints: [any non-obvious constraints found]
```
