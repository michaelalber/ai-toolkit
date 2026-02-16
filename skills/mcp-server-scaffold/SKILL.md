---
name: mcp-server-scaffold
description: Custom MCP server creation with FastMCP pattern and testing. Use when building MCP servers to expose tools, resources, or prompts to AI assistants.
---

# MCP Server Scaffold

> "A good interface is like a good joke: if you have to explain it, it isn't that good."
> -- adapted from the Unix philosophy

## Core Philosophy

This skill guides the creation of Model Context Protocol (MCP) servers using the Python `mcp` SDK and the FastMCP pattern. MCP servers expose **tools**, **resources**, and **prompts** to AI assistants through a standardized protocol.

**Non-Negotiable Constraints:**
1. Every tool MUST have clear, descriptive naming that communicates its purpose
2. Every tool MUST validate all inputs before execution using Pydantic models or type annotations
3. Every tool MUST handle errors gracefully and return structured error responses -- never expose raw exceptions
4. Transport layer MUST be abstracted from business logic -- handlers work identically across stdio, SSE, and streamable HTTP
5. Every tool MUST have corresponding tests that verify behavior, edge cases, and error conditions
6. Security boundaries MUST be enforced -- tools never access resources outside their declared scope

## Domain Principles Table

| # | Principle | Description | Priority |
|---|-----------|-------------|----------|
| 1 | **Tool Naming Clarity** | Tool names use `verb_noun` convention (e.g., `get_user`, `search_documents`). Names are the primary documentation for AI consumers. | Critical |
| 2 | **Schema Validation** | All tool inputs are validated through type annotations or Pydantic models. Invalid inputs are rejected before handler execution with clear error messages. | Critical |
| 3 | **Error Propagation** | Errors are returned as structured MCP error responses, not raised as exceptions. Use `ctx.error()` for operational errors. Reserve exceptions for truly unexpected failures. | Critical |
| 4 | **Transport Abstraction** | Server logic is transport-agnostic. The same tool handlers work across stdio, SSE, and streamable HTTP without modification. Transport is a deployment concern, not a design concern. | High |
| 5 | **Idempotent Operations** | Read-only tools are naturally idempotent. Write tools document their idempotency guarantees. Repeated calls with the same input produce consistent outcomes. | High |
| 6 | **Resource Lifecycle** | Resources have clear URIs, predictable content types, and well-defined freshness semantics. Resource templates use URI patterns for parameterized access. | High |
| 7 | **Prompt Templating** | Prompts declare their arguments explicitly. Templates produce well-structured messages with clear roles. Prompts are composable building blocks, not monolithic instructions. | Medium |
| 8 | **Security Boundaries** | Tools operate within declared scopes. File access is restricted to allowed directories. Network calls go only to approved endpoints. Secrets never appear in tool responses. | Critical |
| 9 | **Logging and Observability** | All tool invocations log input parameters (sanitized), execution duration, and outcome. Use `ctx.info()`, `ctx.warning()`, and `ctx.error()` for structured logging. Progress reporting uses `ctx.report_progress()`. | High |
| 10 | **Graceful Degradation** | When external dependencies fail, tools return meaningful partial results or clear error messages rather than crashing. Timeout handling is explicit. | Medium |

## Workflow

### MCP Server Development Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│   ┌──────────┐    ┌──────────┐    ┌───────────┐                 │
│   │  Design  │───>│ Scaffold │───>│ Implement │                 │
│   │  Tools   │    │  Server  │    │ Handlers  │                 │
│   └──────────┘    └──────────┘    └─────┬─────┘                 │
│                                         │                        │
│                                         v                        │
│   ┌──────────┐    ┌──────────┐    ┌───────────┐                 │
│   │  Deploy  │<───│Integration│<──│  Test w/  │                 │
│   │          │    │  Test     │    │ Inspector │                 │
│   └──────────┘    └──────────┘    └───────────┘                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Step-by-Step

1. **Design Tools** -- Identify what capabilities the server exposes. Classify each as tool, resource, or prompt.
2. **Scaffold Server** -- Create the FastMCP server instance, configure transport, set up project structure.
3. **Implement Handlers** -- Write tool handlers with input validation, error handling, and logging.
4. **Test with Inspector** -- Use `mcp dev` to interactively validate each tool via the MCP Inspector.
5. **Integration Test** -- Write pytest-based tests that exercise tools end-to-end.
6. **Deploy** -- Configure the appropriate transport and deploy (stdio for CLI, SSE/HTTP for networked).

### Tool Design Decision Tree

```
What capability does the AI need?
│
├── Perform an ACTION or COMPUTATION?
│   └── Use @mcp.tool()
│       Examples: search_database, send_email, calculate_metrics
│
├── Access DATA that changes over time?
│   └── Use @mcp.resource()
│       Examples: config://settings, db://users/{id}, log://recent
│
├── Generate a STRUCTURED PROMPT for the LLM?
│   └── Use @mcp.prompt()
│       Examples: review_code, summarize_document, debug_error
│
└── Unsure?
    └── Default to @mcp.tool() -- tools are the most flexible primitive
```

## State Block Format

Maintain state across conversation turns using this block:

```
<mcp-server-state>
step: [Design Tools | Scaffold Server | Implement Handlers | Test with Inspector | Integration Test | Deploy]
server_name: [name of the MCP server]
transport: [stdio | sse | streamable-http]
tools_defined: [count of tools defined]
tools_tested: [count of tools with passing tests]
last_action: [what was just completed]
next_action: [what should happen next]
blockers: [any issues preventing progress]
</mcp-server-state>
```

### Example State Progression

```
<mcp-server-state>
step: Implement Handlers
server_name: document-search-server
transport: stdio
tools_defined: 3
tools_tested: 1
last_action: Implemented search_documents tool with input validation
next_action: Implement get_document_by_id tool
blockers: none
</mcp-server-state>
```

## Output Templates

### Server Scaffold Template

```python
# server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("server-name")


@mcp.tool()
async def tool_name(param: str) -> str:
    """Tool description for AI consumers."""
    # Implementation
    return result


if __name__ == "__main__":
    mcp.run()
```

### Tool Implementation Template

```python
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP, Context


class SearchInput(BaseModel):
    query: str = Field(description="Search query string")
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum results to return")


@mcp.tool()
async def search_documents(query: str, max_results: int = 10, ctx: Context = None) -> str:
    """Search documents by keyword query.

    Returns matching documents with relevance scores.
    """
    if ctx:
        ctx.info(f"Searching for: {query}, max_results={max_results}")

    try:
        results = await perform_search(query, max_results)
        if ctx:
            ctx.info(f"Found {len(results)} results")
        return format_results(results)
    except SearchError as e:
        if ctx:
            ctx.error(f"Search failed: {e}")
        return f"Error: Search failed - {e}"
```

### Test Setup Template

```python
# tests/test_server.py
import pytest
from mcp.server.fastmcp import FastMCP


@pytest.fixture
def mcp_server():
    """Create a fresh MCP server instance for testing."""
    from server import mcp
    return mcp


@pytest.mark.asyncio
async def test_tool_returns_expected_result(mcp_server):
    """Test that tool produces correct output for valid input."""
    result = await mcp_server.call_tool("tool_name", {"param": "value"})
    assert "expected" in result[0].text
```

## AI Discipline Rules

### CRITICAL: Always Validate Tool Inputs

Before processing any tool invocation:
1. All required parameters MUST be present
2. All parameter types MUST match their declared types
3. All parameter values MUST fall within declared constraints (min, max, pattern)
4. Validation failures MUST return clear, actionable error messages

```python
# WRONG: No validation
@mcp.tool()
async def delete_file(path: str) -> str:
    os.remove(path)
    return "Deleted"

# RIGHT: Validated and constrained
@mcp.tool()
async def delete_file(path: str, ctx: Context = None) -> str:
    """Delete a file within the allowed workspace directory."""
    resolved = Path(path).resolve()
    if not resolved.is_relative_to(WORKSPACE_DIR):
        return "Error: Path is outside the allowed workspace directory"
    if not resolved.exists():
        return f"Error: File not found: {path}"
    resolved.unlink()
    if ctx:
        ctx.info(f"Deleted file: {resolved}")
    return f"Successfully deleted: {resolved.name}"
```

### CRITICAL: Never Expose Raw Exceptions

Tool handlers MUST catch exceptions and return structured error messages:

```python
# WRONG: Exception bubbles up to transport layer
@mcp.tool()
async def query_database(sql: str) -> str:
    return db.execute(sql)  # Raw exception if DB is down

# RIGHT: Caught and wrapped
@mcp.tool()
async def query_database(sql: str, ctx: Context = None) -> str:
    """Execute a read-only SQL query against the analytics database."""
    try:
        result = await db.execute(sql)
        return format_query_result(result)
    except ConnectionError:
        if ctx:
            ctx.error("Database connection failed")
        return "Error: Database is currently unavailable. Please try again later."
    except QuerySyntaxError as e:
        return f"Error: Invalid SQL syntax - {e}"
```

### CRITICAL: Always Write Tool Tests

Every tool MUST have tests covering:
1. **Happy path** -- valid inputs produce expected outputs
2. **Edge cases** -- empty inputs, boundary values, special characters
3. **Error cases** -- invalid inputs, missing dependencies, timeout scenarios
4. **Input validation** -- type mismatches, out-of-range values

Do NOT ship a tool without at least one test per category above.

### CRITICAL: Never Skip MCP Inspector Validation

Before declaring a tool complete:
1. Run `mcp dev server.py` to launch the MCP Inspector
2. Invoke each tool with sample inputs in the Inspector UI
3. Verify the response format matches expectations
4. Test error cases interactively
5. Confirm the tool description and parameter schemas appear correctly

If the Inspector is not available, document the gap and create an issue.

## Anti-Patterns Table

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| **God tool that does everything** | Overloaded tools confuse AI consumers, make testing difficult, and violate single-responsibility | Split into focused tools: `search_users`, `get_user`, `create_user` instead of `manage_users` |
| **Missing input schemas** | AI cannot construct valid requests without knowing parameter types and constraints | Always declare types, use `Field()` for descriptions and constraints |
| **Exposing raw exceptions** | Stack traces leak implementation details, confuse AI consumers, and may expose secrets | Catch exceptions, return structured error strings |
| **Transport-coupled logic** | Business logic tied to a specific transport cannot be reused or tested in isolation | Keep handlers transport-agnostic; transport is configured at startup |
| **Stateful tools without documentation** | Tools that depend on prior invocations create hidden coupling that AI cannot reason about | Document state requirements in tool descriptions, prefer stateless designs |
| **Ignoring Context parameter** | Skipping `ctx` means no logging, no progress reporting, and no resource access | Accept `Context` parameter and use it for logging and progress |
| **Overly broad resource URIs** | Resources like `data://everything` provide no structure for AI navigation | Use specific URI patterns: `users://{id}`, `config://database` |
| **Hardcoded configuration** | Secrets, endpoints, and paths baked into code cannot be changed per deployment | Use environment variables or configuration files, never hardcode |

## Error Recovery

### Transport Connection Errors

```
Problem: Client cannot connect to MCP server
Actions:
1. Verify the transport configuration matches client expectations
2. For stdio: ensure the server process starts without errors
3. For SSE: check that the port is available and not blocked by firewall
4. For streamable HTTP: verify the endpoint URL and CORS settings
5. Check server logs for startup errors
6. Test with: mcp dev server.py
```

### Schema Validation Failures

```
Problem: Client sends invalid parameters, tool rejects input
Actions:
1. Review the error message returned to the client
2. Verify parameter types match the tool's declared schema
3. Check for missing required parameters
4. Verify value constraints (min, max, pattern) are documented in Field()
5. Test the tool in MCP Inspector with the failing input
6. If schema is ambiguous, improve Field descriptions
```

### Tool Execution Errors

```
Problem: Tool handler raises an unhandled exception
Actions:
1. Check server logs for the exception traceback
2. Identify which dependency or operation failed
3. Add a try/except block for the specific exception type
4. Return a structured error message to the client
5. Add a test case for the failure scenario
6. Re-test with MCP Inspector to verify error response format
```

### Resource Not Found Errors

```
Problem: Client requests a resource URI that does not exist
Actions:
1. Verify the URI pattern matches a registered resource or resource template
2. Check that template parameters are valid (e.g., user ID exists)
3. Return a clear "not found" message rather than an empty response
4. Log the missing resource request for debugging
5. Consider adding a resource listing endpoint for discovery
```

### Server Startup Failures

```
Problem: MCP server fails to start or crashes on initialization
Actions:
1. Check for import errors in server.py
2. Verify all dependencies are installed (pip install mcp)
3. Check for port conflicts if using SSE or HTTP transport
4. Validate environment variables are set correctly
5. Run server.py directly with Python to see error output
6. Check Python version compatibility (3.10+ required)
```

## Integration with Other Skills

### RAG Pipeline (`rag-pipeline-python`)

MCP servers are natural interfaces for RAG pipelines. Expose retrieval and generation as tools:

```python
@mcp.tool()
async def search_knowledge_base(query: str, top_k: int = 5) -> str:
    """Search the knowledge base using semantic similarity."""
    results = await rag_pipeline.retrieve(query, top_k=top_k)
    return format_results(results)

@mcp.resource("kb://documents/{doc_id}")
async def get_document(doc_id: str) -> str:
    """Retrieve a specific document from the knowledge base."""
    return await rag_pipeline.get_document(doc_id)
```

When building MCP servers that wrap RAG functionality, follow the `rag-pipeline-python` skill for retrieval quality patterns and the MCP server scaffold for the transport/interface layer.

### Ollama Model Workflow (`ollama-model-workflow`)

MCP servers can front local Ollama models, providing a standardized interface for AI-to-AI communication:

```python
@mcp.tool()
async def generate_with_ollama(prompt: str, model: str = "llama3") -> str:
    """Generate text using a local Ollama model."""
    response = await ollama_client.generate(model=model, prompt=prompt)
    return response["response"]

@mcp.tool()
async def list_available_models() -> str:
    """List all Ollama models available on this machine."""
    models = await ollama_client.list()
    return "\n".join(m["name"] for m in models["models"])
```

When the MCP server wraps Ollama inference, follow the `ollama-model-workflow` skill for model selection, prompt formatting, and performance tuning. The MCP layer handles transport and schema; the Ollama workflow handles model-specific concerns.
