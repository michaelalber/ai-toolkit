# Jira Review Skill - Executive Summary

## Purpose

The **jira-review** skill is an automated quality gate that reviews Jira issues before implementation begins. It addresses a fundamental truth in software development: **unclear requirements are the root cause of most project failures**.

## What It Does

When a developer fetches a Jira issue, the skill automatically:

1. **Extracts Requirements** - Parses acceptance criteria, definition of done, and user stories from issue descriptions
2. **Scores Complexity** - Evaluates the issue across 5 weighted dimensions (scope, clarity, technical uncertainty, dependencies, estimation confidence)
3. **Provides a Recommendation** - Categorizes issues as:
   - **READY TO IMPLEMENT** (< 40% complexity) - Clear requirements, proceed with development
   - **NEEDS CLARIFICATION** (40-70% complexity) - Generates specific questions to resolve gaps
   - **NEEDS PLANNING MODE** (> 70% complexity) - Recommends breaking down before implementation

## Business Value

| Benefit | Impact |
|---------|--------|
| Prevents wasted effort | Catches ambiguity early, reducing rework |
| Surfaces hidden complexity | Identifies technical risks before they become blockers |
| Ensures testability | Clear acceptance criteria enable test-driven development |
| Aligns expectations | Questions asked upfront prevent misunderstandings later |

## Key Features

- **Automated activation** when Jira issues are fetched via MCP tools
- **Structured output** with complexity scores, extracted requirements, and actionable next steps
- **Question templates** for efficiently gathering missing information
- **Integration points** with TDD workflow for ready-to-implement issues

## Complexity Scoring Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Scope Breadth | 1.5 | Number of components/systems affected |
| Requirements Clarity | 1.5 | Specificity and completeness of AC/DoD |
| Technical Uncertainty | 1.2 | New tech, integrations, unknowns |
| Dependencies | 1.0 | External team/system dependencies |
| Estimation Confidence | 1.0 | Presence of sizing/story points |

## Example Outcomes

| Issue Type | Complexity | Recommendation |
|------------|------------|----------------|
| Well-defined "Add logout button" | 25% (Low) | READY TO IMPLEMENT |
| Vague "Make it faster" | Unable to assess | NEEDS CLARIFICATION (4 specific questions generated) |
| Complex "Real-time notifications" | 82% (High) | NEEDS PLANNING MODE |

## Integration with Development Workflow

```
Jira Issue Fetched
        │
        ▼
┌───────────────────┐
│  jira-review      │
│  skill activates  │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Complexity        │
│ Assessment        │
└───────────────────┘
        │
        ├──────────────────┬──────────────────┐
        ▼                  ▼                  ▼
   < 40%              40-70%              > 70%
   GREEN              YELLOW               RED
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ READY TO     │   │ NEEDS        │   │ NEEDS        │
│ IMPLEMENT    │   │ CLARIFICATION│   │ PLANNING     │
│              │   │              │   │ MODE         │
│ → /tdd-cycle │   │ → Questions  │   │ → Breakdown  │
└──────────────┘   └──────────────┘   └──────────────┘
```

## Summary

The jira-review skill reduces project risk by ensuring requirements are clear, complete, and actionable before any code is written. By catching ambiguity early, teams avoid costly rework and deliver with higher confidence.
