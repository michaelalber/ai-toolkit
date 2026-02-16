---
name: rag-pipeline-dotnet
description: Implements RAG (Retrieval-Augmented Generation) pipelines using Microsoft Semantic Kernel for .NET applications with federal compliance and air-gapped deployment support. Use when building RAG .NET, Semantic Kernel RAG, vector search .NET, document QA .NET, knowledge base .NET, AI search .NET, embedding pipeline, or retrieval-augmented generation in C#.
---

# RAG Pipeline (.NET / Semantic Kernel)

> "RAG combines the power of large language models with your organization's specific knowledge, providing accurate, contextual responses grounded in your data."

> "The quality of your RAG system is bounded by the quality of your retrieval, not the quality of your generation model." -- Jerry Liu, creator of LlamaIndex

This skill guides implementation of RAG pipelines using Microsoft Semantic Kernel for .NET applications, with federal compliance considerations and air-gapped deployment patterns.

## Core Philosophy

RAG is the primary pattern for grounding LLM responses in organizational knowledge. Rather than fine-tuning models on proprietary data, RAG retrieves relevant documents at query time and injects them as context for generation. Microsoft Semantic Kernel serves as the .NET orchestration layer, providing abstractions over embedding models, vector stores, and chat completion services.

**.NET is the right choice for RAG when:**
- The deployment target is an enterprise or federal environment with existing .NET infrastructure
- FedRAMP, FISMA, or DOE compliance requirements mandate authorized cloud services and audit trails
- The team's primary expertise is C# and the .NET ecosystem
- Air-gapped or disconnected operation is required (via Ollama + local vector stores)

**Non-Negotiable Constraints:**
1. Retrieval quality MUST be measured before generation is tuned -- poor retrieval means poor answers regardless of LLM
2. Chunk size and overlap MUST align with the embedding model's context window -- silent truncation destroys meaning
3. Every pipeline MUST include citation and source attribution in generated responses
4. Federal deployments MUST use FIPS-compliant models and FedRAMP-authorized services
5. Document classification MUST be validated before ingestion -- classified data cannot enter the RAG system

## Domain Principles Table

| # | Principle | Description | Priority |
|---|-----------|-------------|----------|
| 1 | **Retrieval Quality Over Generation Quality** | The ceiling of RAG output is set by retrieval, not generation. Measure precision@k and relevance scores before tuning prompts or switching LLMs. Irrelevant context degrades output more than no context at all. | Critical |
| 2 | **Chunk Size Optimization** | Chunks must be self-contained units of meaning sized to fit the embedding model's context window. Too large and they exceed token limits (silent truncation). Too small and they lose semantic coherence. Match chunk size to corpus type and model capacity. | Critical |
| 3 | **Embedding Model Selection** | The embedding model determines the retrieval ceiling. Evaluate on domain-specific queries, not general benchmarks. See `references/embedding-models.md` for options and performance characteristics. | Critical |
| 4 | **Vector Store Selection** | Choose based on deployment environment, compliance requirements, and operational capacity. Azure AI Search for FedRAMP cloud; Qdrant or pgvector for air-gapped. See `references/vector-store-options.md`. | High |
| 5 | **Semantic + Keyword Hybrid Search** | Pure vector similarity misses exact-match queries (error codes, part numbers). Combine semantic search with keyword (BM25) search when the corpus contains identifiers, acronyms, or technical terms. Azure AI Search supports this natively. | High |
| 6 | **Prompt Engineering for Grounded Responses** | The system prompt must constrain the LLM to answer only from provided context. Include explicit instructions to cite sources and to say "I don't know" when context is insufficient. | Critical |
| 7 | **Citation and Provenance** | Every generated answer must trace back to specific source chunks. Include document ID, section, and relevance score in the response. This is a NIST AI RMF transparency requirement for federal systems. | High |
| 8 | **Hallucination Detection** | Monitor for answers that contain claims not present in retrieved context. Implement post-generation verification: compare answer claims against source chunk content. Flag and log divergences. | High |
| 9 | **Federal Data Handling** | Validate data classification before ingestion. CUI requires access controls and audit trails. Classified data is never eligible for RAG. See `references/federal-ai-compliance.md`. | Critical |
| 10 | **Air-Gapped Deployment** | Support disconnected environments with Ollama (local LLM + embeddings) and on-premise vector stores (Qdrant, pgvector). No external API calls. FIPS compliance depends on host OS configuration. | High |

## Workflow

### RAG Pipeline Lifecycle

```
+-----------------------------------------------------------------------+
|                   .NET RAG PIPELINE WORKFLOW                           |
|                                                                       |
|  +-----------+   +--------+   +-------+   +----------+   +----------+|
|  |1.CONFIGURE|-->|2.INGEST|-->|3.INDEX|-->|4.RETRIEVE|-->|5.EVALUATE||
|  +-----------+   +--------+   +-------+   +----------+   +----------+|
|       |                                        |               |      |
|       |                                        v               |      |
|       |                                  +----------+          |      |
|       |                                  | GENERATE |          |      |
|       |                                  +----------+          |      |
|       |                                                        |      |
|       +--------------------------------------------------------+      |
|                        (iterate if needed)                            |
+-----------------------------------------------------------------------+
```

### Phase 1: CONFIGURE -- Semantic Kernel Setup

Set up Semantic Kernel with the chosen LLM provider, embedding model, and vector store. The flow is: User Query -> Query Embedding -> Vector Search -> Relevant Chunks -> LLM Generation -> Response.

**Project Setup:**

```xml
<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <!-- Semantic Kernel Core -->
    <PackageReference Include="Microsoft.SemanticKernel" Version="1.25.0" />

    <!-- Memory/Vector Store Connectors -->
    <PackageReference Include="Microsoft.SemanticKernel.Connectors.AzureAISearch" Version="1.25.0-alpha" />
    <PackageReference Include="Microsoft.SemanticKernel.Connectors.Qdrant" Version="1.25.0-alpha" />
    <PackageReference Include="Microsoft.SemanticKernel.Connectors.Postgres" Version="1.25.0-alpha" />

    <!-- Document Processing -->
    <PackageReference Include="Microsoft.SemanticKernel.Plugins.Document" Version="1.25.0-alpha" />

    <!-- AI Providers -->
    <PackageReference Include="Microsoft.SemanticKernel.Connectors.AzureOpenAI" Version="1.25.0" />
    <PackageReference Include="Microsoft.SemanticKernel.Connectors.OpenAI" Version="1.25.0" />
  </ItemGroup>

</Project>
```

**Program.cs Setup (Azure OpenAI):**

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddSingleton(sp =>
{
    var kernelBuilder = Kernel.CreateBuilder();
    kernelBuilder.AddAzureOpenAIChatCompletion(
        deploymentName: builder.Configuration["AzureOpenAI:ChatDeployment"]!,
        endpoint: builder.Configuration["AzureOpenAI:Endpoint"]!,
        apiKey: builder.Configuration["AzureOpenAI:ApiKey"]!);
    kernelBuilder.AddAzureOpenAITextEmbeddingGeneration(
        deploymentName: builder.Configuration["AzureOpenAI:EmbeddingDeployment"]!,
        endpoint: builder.Configuration["AzureOpenAI:Endpoint"]!,
        apiKey: builder.Configuration["AzureOpenAI:ApiKey"]!);
    return kernelBuilder.Build();
});

// Vector Store -- choose one (see references/vector-store-options.md)
builder.Services.AddSingleton<ISemanticTextMemory>(sp =>
{
    var embeddingGenerator = sp.GetRequiredService<Kernel>()
        .GetRequiredService<ITextEmbeddingGenerationService>();
    return new MemoryBuilder()
        .WithAzureAISearchMemoryStore(
            builder.Configuration["AzureSearch:Endpoint"]!,
            builder.Configuration["AzureSearch:ApiKey"]!)
        .WithTextEmbeddingGeneration(embeddingGenerator).Build();
});

builder.Services.AddScoped<IRagService, RagService>();
```

**Air-Gapped Configuration (Ollama):**

```csharp
kernelBuilder.AddOllamaChatCompletion(
    modelId: "llama3", endpoint: new Uri("http://localhost:11434"));
kernelBuilder.AddOllamaTextEmbeddingGeneration(
    modelId: "nomic-embed-text", endpoint: new Uri("http://localhost:11434"));
```

**appsettings.json:**

```json
{
  "AzureOpenAI": {
    "Endpoint": "https://your-resource.openai.azure.com/",
    "ApiKey": "your-api-key",
    "ChatDeployment": "gpt-4",
    "EmbeddingDeployment": "text-embedding-ada-002"
  },
  "AzureSearch": {
    "Endpoint": "https://your-search.search.windows.net",
    "ApiKey": "your-search-key",
    "IndexName": "documents"
  },
  "Rag": { "ChunkSize": 500, "ChunkOverlap": 100, "TopK": 5, "MinRelevanceScore": 0.7 }
}
```

### Phase 2: INGEST -- Document Processing and Chunking

Load documents, validate content extraction, and split into semantically coherent chunks. See the full `RagService` implementation below for the `IngestDocumentAsync`, `ChunkText`, and `SearchAsync` methods.

### Phase 3: INDEX -- Embedding and Vector Store

Embeddings are generated automatically by Semantic Kernel's `ISemanticTextMemory` during `SaveInformationAsync`. The vector store connector handles index creation and upsert. See `references/vector-store-options.md` and `references/embedding-models.md`.

### Phase 4: RETRIEVE -- Query Processing and Ranking

Process user queries through embedding, similarity search (with `MinRelevanceScore` threshold), and context assembly. The `SearchAsync` method returns ranked results by relevance.

### Phase 5: EVALUATE -- Relevance Scoring and Accuracy

Before deploying, test retrieval quality with representative queries. Verify that retrieved chunks are relevant and that generated answers are grounded in context. See the Output Templates section for evaluation report format.

## RAG Service Implementation

```csharp
// Services/RagService.cs
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Memory;
using Microsoft.SemanticKernel.ChatCompletion;

namespace MyApp.Services;

public interface IRagService
{
    Task<string> AskAsync(string question, string collection, CancellationToken ct = default);
    Task IngestDocumentAsync(string documentPath, string collection, CancellationToken ct = default);
    Task<IEnumerable<MemoryQueryResult>> SearchAsync(string query, string collection,
        int limit = 5, CancellationToken ct = default);
}

public class RagService : IRagService
{
    private readonly Kernel _kernel;
    private readonly ISemanticTextMemory _memory;
    private readonly ILogger<RagService> _logger;
    private readonly RagSettings _settings;

    public RagService(Kernel kernel, ISemanticTextMemory memory,
        IOptions<RagSettings> settings, ILogger<RagService> logger)
    {
        _kernel = kernel; _memory = memory;
        _settings = settings.Value; _logger = logger;
    }

    public async Task<string> AskAsync(string question, string collection, CancellationToken ct = default)
    {
        _logger.LogInformation("RAG query: {Question}", question);
        var searchResults = await SearchAsync(question, collection, _settings.TopK, ct);
        var relevantChunks = searchResults.ToList();

        if (!relevantChunks.Any())
            return "I don't have enough information to answer that question.";

        var context = BuildContext(relevantChunks);
        var response = await GenerateResponseAsync(question, context, ct);
        _logger.LogInformation("RAG response generated with {ChunkCount} context chunks", relevantChunks.Count);
        return response;
    }

    public async Task IngestDocumentAsync(string documentPath, string collection, CancellationToken ct = default)
    {
        _logger.LogInformation("Ingesting document: {Path}", documentPath);
        var content = await File.ReadAllTextAsync(documentPath, ct);
        var chunks = ChunkText(content, _settings.ChunkSize, _settings.ChunkOverlap);
        var documentId = Path.GetFileNameWithoutExtension(documentPath);
        var tasks = chunks.Select((chunk, index) =>
            _memory.SaveInformationAsync(collection: collection, text: chunk,
                id: $"{documentId}_{index}",
                description: $"Chunk {index} from {documentPath}",
                cancellationToken: ct));
        await Task.WhenAll(tasks);
        _logger.LogInformation("Ingested {ChunkCount} chunks from {Path}", chunks.Count, documentPath);
    }

    public async Task<IEnumerable<MemoryQueryResult>> SearchAsync(
        string query, string collection, int limit = 5, CancellationToken ct = default)
    {
        var results = new List<MemoryQueryResult>();
        await foreach (var result in _memory.SearchAsync(
            collection: collection, query: query, limit: limit,
            minRelevanceScore: _settings.MinRelevanceScore, cancellationToken: ct))
            results.Add(result);
        return results;
    }

    private static List<string> ChunkText(string text, int chunkSize, int overlap)
    {
        var chunks = new List<string>();
        var sentences = text.Split(new[] { ". ", ".\n", ".\r\n" }, StringSplitOptions.RemoveEmptyEntries);
        var currentChunk = new StringBuilder();
        var overlapBuffer = new Queue<string>();
        foreach (var sentence in sentences)
        {
            if (currentChunk.Length + sentence.Length > chunkSize && currentChunk.Length > 0)
            {
                chunks.Add(currentChunk.ToString().Trim());
                currentChunk.Clear();
                while (overlapBuffer.Count > 0 && currentChunk.Length < overlap)
                    currentChunk.Append(overlapBuffer.Dequeue()).Append(". ");
            }
            currentChunk.Append(sentence).Append(". ");
            overlapBuffer.Enqueue(sentence);
            while (overlapBuffer.Count > 3) overlapBuffer.Dequeue();
        }
        if (currentChunk.Length > 0) chunks.Add(currentChunk.ToString().Trim());
        return chunks;
    }

    private static string BuildContext(IEnumerable<MemoryQueryResult> results)
    {
        var sb = new StringBuilder();
        sb.AppendLine("Relevant information:\n");
        foreach (var result in results)
        {
            sb.AppendLine($"[Source: {result.Metadata.Description}]");
            sb.AppendLine(result.Metadata.Text); sb.AppendLine();
        }
        return sb.ToString();
    }

    private async Task<string> GenerateResponseAsync(string question, string context, CancellationToken ct)
    {
        var chatService = _kernel.GetRequiredService<IChatCompletionService>();
        var chatHistory = new ChatHistory();
        chatHistory.AddSystemMessage("""
            You are a helpful assistant that answers questions based on the provided context.
            Only use information from the context to answer. If the context doesn't contain
            relevant information, say so. Cite your sources when possible.
            """);
        chatHistory.AddUserMessage($"""
            Context:
            {context}

            Question: {question}

            Please answer the question based on the context above.
            """);
        var response = await chatService.GetChatMessageContentAsync(chatHistory, cancellationToken: ct);
        return response.Content ?? "Unable to generate response.";
    }
}

public class RagSettings
{
    public int ChunkSize { get; set; } = 500;
    public int ChunkOverlap { get; set; } = 100;
    public int TopK { get; set; } = 5;
    public double MinRelevanceScore { get; set; } = 0.7;
}
```

## API Endpoints

```csharp
// Features/Rag/RagEndpoints.cs
public static class RagEndpoints
{
    public static IEndpointRouteBuilder MapRagEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/rag")
            .WithTags("RAG")
            .RequireAuthorization();

        group.MapPost("/ask", AskQuestion)
            .WithSummary("Ask a question using RAG")
            .Accepts<AskRequest>("application/json")
            .Produces<AskResponse>(200);

        group.MapPost("/ingest", IngestDocument)
            .WithSummary("Ingest a document into the knowledge base")
            .Accepts<IngestRequest>("application/json")
            .Produces(204);

        group.MapPost("/search", SearchDocuments)
            .WithSummary("Search for relevant documents")
            .Accepts<SearchRequest>("application/json")
            .Produces<SearchResponse>(200);

        return app;
    }

    private static async Task<IResult> AskQuestion(
        AskRequest request, IRagService ragService, CancellationToken ct)
    {
        var answer = await ragService.AskAsync(request.Question, request.Collection, ct);
        return Results.Ok(new AskResponse(answer));
    }

    private static async Task<IResult> IngestDocument(
        IngestRequest request, IRagService ragService, CancellationToken ct)
    {
        await ragService.IngestDocumentAsync(request.DocumentPath, request.Collection, ct);
        return Results.NoContent();
    }

    private static async Task<IResult> SearchDocuments(
        SearchRequest request, IRagService ragService, CancellationToken ct)
    {
        var results = await ragService.SearchAsync(request.Query, request.Collection, request.Limit, ct);
        return Results.Ok(new SearchResponse(results.Select(r => new SearchResult(
            r.Metadata.Id, r.Metadata.Text, r.Relevance))));
    }
}

public record AskRequest(string Question, string Collection);
public record AskResponse(string Answer);
public record IngestRequest(string DocumentPath, string Collection);
public record SearchRequest(string Query, string Collection, int Limit = 5);
public record SearchResponse(IEnumerable<SearchResult> Results);
public record SearchResult(string Id, string Text, double Relevance);
```

## Federal Compliance

For federal deployments, wrap the base `RagService` with classification validation and audit logging. See `references/federal-ai-compliance.md` for full implementation details including:

- **Data Classification**: Validate documents before ingestion (Unclassified, CUI, Classified)
- **CUI Handling**: Separate collections, CUI markings on responses, query/response classification
- **Audit Logging**: Who, what, when, where for every query and response
- **FedRAMP Services**: Use Azure Government endpoints (`.azure.us`) with authorized services
- **NIST AI RMF**: Governance, risk assessment, performance monitoring, transparency
- **Access Control**: Role-based collection access with clearance-level enforcement

```csharp
public class FederalRagService : RagService
{
    public override async Task IngestDocumentAsync(string documentPath, string collection, CancellationToken ct)
    {
        var classification = await ValidateClassificationAsync(documentPath);
        if (classification == DataClassification.Classified)
            throw new InvalidOperationException("Classified documents cannot be processed by RAG system");
        if (classification == DataClassification.CUI)
        {
            collection = $"cui_{collection}";
            _logger.LogWarning("Processing CUI document: {Path}", documentPath);
        }
        await base.IngestDocumentAsync(documentPath, collection, ct);
        await _auditService.LogDocumentIngestionAsync(documentPath, classification);
    }
}
```

## State Block

Maintain state across conversation turns:

```
<rag-dotnet-state>
mode: [CONFIGURE | INGEST | INDEX | RETRIEVE | EVALUATE]
vector_store: [azure-ai-search | qdrant | chromadb | pgvector | none]
embedding_model: [text-embedding-3-small | nomic-embed-text | mxbai-embed-large | none]
generation_model: [gpt-4 | llama3 | none]
documents_ingested: [count or none]
index_built: [true | false]
retrieval_tested: [true | false]
federal_compliant: [true | false | n/a]
last_action: [what was just done]
next_action: [what should happen next]
</rag-dotnet-state>
```

**Example:**

```
<rag-dotnet-state>
mode: RETRIEVE
vector_store: azure-ai-search
embedding_model: text-embedding-3-small
generation_model: gpt-4
documents_ingested: 150
index_built: true
retrieval_tested: false
federal_compliant: true
last_action: Completed document ingestion for policies collection
next_action: Run retrieval evaluation with 10 representative queries
</rag-dotnet-state>
```

## Output Templates

### Pipeline Configuration Summary

```markdown
## RAG Implementation: [Project Name]
**Vector Store**: [Azure AI Search | Qdrant | pgvector] | **LLM**: [Azure OpenAI | Ollama]
**Embedding**: [text-embedding-3-small | nomic-embed-text] | **Chunk**: [500/100]

| Collection | Documents | Purpose | | Endpoint | Description |
|------------|-----------|---------|---|----------|-------------|
| policies | 50 | Policies | | POST /api/rag/ask | Question answering |
| procedures | 120 | SOPs | | POST /api/rag/ingest | Document ingestion |
| | | | | POST /api/rag/search | Similarity search |
```

### Ingestion Report

```markdown
## Ingestion Report
**Date**: [date] | **Collection**: [name] | **Embedding Model**: [model]
**Documents Processed**: [count] | **Chunks Generated**: [count] | **Avg Chunk Size**: [chars]

| Document | Chunks | Status |
|----------|--------|--------|
| [filename] | [count] | Success/Failed |
```

### Retrieval Quality Metrics

```markdown
## Retrieval Evaluation Report
**Date**: [date] | **Embedding Model**: [model] | **Vector Store**: [store]

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Precision@5 | [X.XX] | >= 0.70 | PASS/FAIL |
| Avg Relevance | [X.XX] | >= 0.75 | PASS/FAIL |
| Queries with 0 results | [count] | 0 | PASS/FAIL |
```

### Deployment Checklist

```markdown
## RAG Deployment Checklist
- [ ] Vector store connection verified
- [ ] Embedding and generation models accessible and tested
- [ ] All documents ingested successfully
- [ ] Retrieval evaluation passed (precision@k >= 0.70)
- [ ] Out-of-scope queries return "I don't know" (not hallucination)
- [ ] Authentication, authorization, and audit logging configured
- [ ] Federal compliance verified (if applicable)
- [ ] Air-gapped fallback tested (if applicable)
- Security: [JWT | Azure AD] | Classification: [Handled | N/A] | Audit: [Enabled | Disabled]
```

## AI Discipline Rules

### CRITICAL: Always Test Retrieval Before Generation

Before tuning prompts or switching generation models, verify retrieval quality first. Poor retrieval means poor answers regardless of LLM quality.

```
STOP! Before tuning generation:
1. Run SearchAsync with 10+ representative queries
2. Inspect relevance scores -- are they above MinRelevanceScore?
3. Spot-check 3-5 retrieved chunks manually -- are they actually relevant?
4. If retrieval is poor, fix chunking or embedding model FIRST
5. Only after retrieval is solid should you tune generation prompts
```

### CRITICAL: Never Skip Chunking Optimization

One chunk size does not fit all document types. PDFs, Markdown, and code require different strategies. Always verify chunk coherence before embedding.

```
MANDATORY before indexing:
1. Inspect 5-10 chunks from different document types
2. Verify chunks are self-contained (not mid-sentence splits)
3. Verify chunks fit within embedding model context window
4. Adjust ChunkSize and ChunkOverlap based on inspection
```

### CRITICAL: Always Include Citation in Generated Responses

The system prompt must instruct the LLM to cite source chunks. Uncited responses cannot be verified and are a compliance failure in federal contexts.

```
MANDATORY in system prompt:
- "Cite the source document for each claim"
- "If context is insufficient, say so explicitly"
- "Do not generate information not present in the context"
```

### CRITICAL: Validate Vector Store Connection Before Ingestion

A failed connection during batch ingestion can leave the index in a partial state. Always write and remove a health-check record (`_healthcheck` collection) before starting batch ingestion. Abort on any connection failure.

### CRITICAL: Use FIPS-Compliant Models for Federal Deployments

For federal systems: use Azure Government endpoints (`.azure.us`), verify FedRAMP authorization of all services, enable FIPS mode on host OS for air-gapped Ollama deployments, and document FIPS compliance status in the deployment checklist.

## Anti-Patterns Table

| Anti-Pattern | Why It Fails | Correct Approach |
|-------------|-------------|------------------|
| **Using the generation model for embedding** | Chat/completion models produce different vector spaces than embedding models; retrieval quality collapses | Use a dedicated embedding model (text-embedding-3-small, nomic-embed-text) |
| **Single chunk size for all document types** | PDFs, Markdown, code, and prose have different structural boundaries; one size splits content at wrong points | Use document-type-specific chunking strategies; inspect chunks before embedding |
| **No retrieval evaluation** | Generation quality is bounded by retrieval; tuning prompts on bad retrieval is wasted effort | Evaluate precision@k and relevance scores with representative queries before touching generation |
| **Ignoring context window limits** | Stuffing too many chunks into the LLM prompt dilutes relevant information and may exceed token limits | Calculate token budget: prompt + context + expected response must fit within model context window |
| **Storing PII/CUI without classification** | Federal compliance violation; data spillage risk if unclassified and classified data share a collection | Validate data classification before ingestion; separate CUI into dedicated collections with access controls |
| **Treating RAG as magic search** | RAG is not a search engine -- it is a knowledge-grounded generation pattern; expecting keyword-search behavior leads to frustration | Set user expectations; implement hybrid search for keyword needs; document what RAG can and cannot do |
| **Hardcoding embedding model without benchmarking** | Different models have different strengths; what works for English prose may fail for technical documents | Benchmark 2-3 embedding models on domain-specific queries before committing to one |
| **No citation or source attribution** | Users cannot verify answers; compliance failure in federal contexts; trust erosion | Include source document ID, chunk description, and relevance score in every response |
| **Batch ingestion without connection validation** | Partial index state if connection fails mid-batch; silent data loss | Test vector store connection before starting ingestion; implement retry with idempotent IDs |
| **Using MinRelevanceScore of 0.0** | Returns every chunk regardless of relevance, flooding the LLM context with noise | Set MinRelevanceScore to 0.7+ and tune based on evaluation results |

## Error Recovery

### Poor Retrieval Quality

```
Problem: precision@k < 0.50 -- retrieved chunks are not relevant
Actions:
1. Inspect retrieved chunks manually for 3-5 queries
2. Check if chunks are too large (exceeding embedding context) or too small (losing coherence)
3. Try a different embedding model (ada-002 -> text-embedding-3-small, or MiniLM -> nomic)
4. For exact-match queries (error codes, IDs), add hybrid search (BM25 + vector)
5. Increase TopK + add re-ranking; re-evaluate after each single change
```

### Embedding Model Mismatch

```
Problem: Vector store rejects embeddings or returns garbage after model change
Actions:
1. Verify dimension match (text-embedding-3-small:1536, nomic:768, mxbai:1024)
2. If you changed models, you MUST rebuild the entire index -- drop, recreate, re-embed
3. Never mix embeddings from different models in the same collection
```

### Vector Store Connection Failures

```
Problem: Vector store unreachable or returning connection errors
Actions:
1. Verify network connectivity and authentication credentials
2. Azure AI Search: verify service running and index exists
3. Qdrant: check Docker (docker ps, docker logs qdrant)
4. pgvector: verify PostgreSQL running and extension installed
5. Implement circuit breaker; return graceful "service unavailable"
```

### Air-Gapped Deployment Issues

```
Problem: Ollama models not responding or producing low-quality embeddings
Actions:
1. Verify Ollama running: curl http://localhost:11434/api/tags
2. Confirm model pulled (ollama list) and VRAM available (~1-2GB for embeddings)
3. Try larger model (nomic-embed-text -> mxbai-embed-large) for quality
4. Increase num_ctx for generation quality; verify local vector store accessible
5. Test full pipeline end-to-end before deploying to disconnected network
```

## Integration with Other Skills

### RAG Pipeline Python (`rag-pipeline-python`)

The Python counterpart to this skill, using LangChain and Ollama. Use when the team's primary language is Python or when leveraging the broader LangChain ecosystem. The core RAG principles (retrieval quality over generation quality, chunking optimization, evaluation before deployment) are identical across both skills.

### Ollama Model Workflow (`ollama-model-workflow`)

Use to select, pull, and benchmark local models for air-gapped RAG deployments. Key integration points:
- **Embedding model selection**: Benchmark `nomic-embed-text` vs `mxbai-embed-large` on domain corpus
- **Generation model selection**: Match `num_ctx` to expected retrieval context size plus prompt overhead
- **Hardware assessment**: Verify VRAM for both embedding and generation models simultaneously

### .NET Security Review - Federal (`dotnet-security-review-federal`)

Use for security and compliance review of RAG pipeline code. Key areas:
- NIST SP 800-53 controls for data access (AC family) and audit logging (AU family)
- FIPS 140-2/3 cryptographic compliance for API connections and data at rest
- CUI handling validation for document ingestion and response generation

### MCP Server Scaffold (`mcp-server-scaffold`)

RAG pipelines are natural backends for MCP server tools. Use the `mcp-server-scaffold` skill to expose search and question-answering as MCP tools that other AI agents can invoke.

## References

- `references/federal-ai-compliance.md` - Federal compliance requirements (NIST AI RMF, FedRAMP, CUI, audit logging)
- `references/vector-store-options.md` - Vector store comparison (Azure AI Search, Qdrant, ChromaDB, pgvector)
- `references/embedding-models.md` - Embedding model options and performance characteristics
