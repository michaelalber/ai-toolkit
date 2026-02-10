# AI Toolkit for Agents

This document provides guidelines and commands for agents operating in this AI toolkit repository.

## Build, Lint, and Test Commands

### General Commands
- `npm run build` - Build the project
- `npm run lint` - Run linting checks
- `npm run test` - Run all tests
- `npm run test:unit` - Run unit tests
- `npm run test:integration` - Run integration tests
- `npm run test:watch` - Watch tests for changes
- `npm run test -- --testNamePattern="pattern"` - Run specific test by name pattern
- `npm run typecheck` - Run TypeScript type checking

### Running Single Tests
- `npm run test -- <test-file-path>` - Run specific test file
- `npm run test -- --testPathPattern="<pattern>"` - Run tests matching pattern
- `npm run test -- --testNamePattern="<name>"` - Run test with specific name

## Code Style Guidelines

### General Principles
- Follow clean code principles with descriptive naming
- Maintain consistent code structure across all modules
- Write tests before code (TDD approach)
- Keep functions small and focused on single responsibilities
- Use meaningful variable and function names (>2 characters)
- Implement comprehensive error handling with meaningful messages

### Formatting
- Use 2-space indentation
- Prefer single quotes for strings
- No trailing whitespace
- Consistent brace placement (1TBS style)
- 80-character line width limit

### Imports
- Group imports: node modules, external libraries, internal modules, local imports
- Sort imports alphabetically within groups
- Use relative paths for local imports
- Avoid wildcard imports (import * as foo)

### Types
- Use TypeScript for type safety
- Prefer interfaces over types for object shapes
- Use union types for multiple possible values
- Mark optional properties with ?
- Use generics for reusable components

### Naming Conventions
- PascalCase for classes and interfaces
- camelCase for functions and variables
- UPPER_SNAKE_CASE for constants
- Prefix abstract classes with Abstract
- Use descriptive names that indicate purpose

### Error Handling
- Use try-catch blocks around asynchronous operations
- Validate inputs early and fail fast
- Implement proper logging for errors
- Use custom error types when appropriate
- Distinguish between expected and unexpected errors

### Documentation
- Document all public APIs with JSDoc
- Add code comments for complex logic
- Keep documentation in sync with code changes
- Include examples for complex functions

## Cursor/Copilot Rules (if applicable)

No specific Cursor or Copilot rules found in this repository. When working with AI coding assistants, follow standard practices of:
- Providing clear, concise prompts
- Including relevant context and code snippets
- Focusing on specific tasks rather than broad requests
- Requesting explicit code changes when needed

This toolkit is organized into skills, agents, and patterns for different domains (TDD, .NET, Edge AI, ML, Architecture, etc.). Agents should maintain consistency with the project structure and guidelines while operating autonomously.