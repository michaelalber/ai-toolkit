# APOSD Principles — Interface Design Scoring Guide

Reference for evaluating interface designs using vocabulary from
*A Philosophy of Software Design* by John Ousterhout.

## Scoring Dimensions

### Information Hiding (1–5, higher = better)

How much complexity is pushed down into the module rather than exposed to callers?

| Score | Meaning |
|-------|---------|
| 5 | Callers never see internal data structures, error formats, or sequencing requirements |
| 3 | Some internal details leak (e.g., callers must know about retry logic or state ordering) |
| 1 | Callers must understand the implementation to use the interface correctly |

### Conceptual Complexity (1–5, lower = better)

How many concepts must a caller understand to use this interface?

| Score | Meaning |
|-------|---------|
| 1 | One concept: call a method, get a result |
| 3 | 2–3 concepts: understand a lifecycle, provide configuration, handle two error modes |
| 5 | 5+ concepts: state machines, multi-step protocols, ordering constraints |

### Cohesion (1–5, higher = better)

Do all methods belong to the same abstraction, or is the interface a grab-bag?

| Score | Meaning |
|-------|---------|
| 5 | Every method operates at the same abstraction level and serves the same purpose |
| 3 | Most methods belong; one or two feel out of place |
| 1 | The interface mixes concerns from different abstraction levels |

### Error Surface (1–5, lower = better)

How many ways can a caller use this interface incorrectly?

| Score | Meaning |
|-------|---------|
| 1 | Misuse is impossible or compile-time prevented |
| 3 | A few obvious wrong uses; errors are detectable at runtime |
| 5 | Many ways to misuse; errors are silent or produce subtle bugs |

## Key APOSD Concepts

**Deep module:** A simple interface that hides a lot of implementation complexity.
The goal of "Design It Twice" is to find the deepest design.

**Shallow module:** An interface that's nearly as complex as its implementation.
Red flag: method count approaches implementation line count.

**Information leakage:** When a design decision is reflected in the interface of two or
more modules — changing the decision requires changing all of them.

**Temporal coupling:** When callers must invoke methods in a specific order. Sign of a
shallow or over-decomposed interface. Push the sequencing into the module.

**General-purpose interface:** One that can be used in situations other than those it
was originally designed for. Prefer general-purpose over special-purpose.
