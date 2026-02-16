---
name: semantic-kernel-rag
description: Sets up RAG (Retrieval-Augmented Generation) pipelines with Microsoft Semantic Kernel. Use when implementing AI-powered search, document Q&A, knowledge bases, or vector search. Triggers on phrases like "rag pipeline", "semantic kernel", "ai search", "vector database", "embeddings", "document qa", "knowledge base".
---

# Semantic Kernel RAG Implementation

> "RAG combines the power of large language models with your organization's specific knowledge, providing accurate, contextual responses grounded in your data."

This skill guides implementation of RAG pipelines using Microsoft Semantic Kernel for .NET applications, with considerations for federal compliance.

## Quick Start

1. **Choose components**: LLM provider, embedding model, vector store
2. **Set up Semantic Kernel**: Configure services and plugins
3. **Implement ingestion**: Document processing → embeddings → vector store
4. **Build retrieval**: Query embedding → similarity search → context
5. **Create chat**: Combine retrieval with LLM generation

## Architecture Overview

```
                                    ┌─────────────────┐
                                    │   User Query    │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │ Query Embedding │
                                    │  (Text → Vector)│
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │  Vector Search  │
                                    │ (Similarity)    │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │ Relevant Chunks │
                                    │   (Context)     │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │      LLM        │
                                    │ (Generate Answer│
                                    │  with Context)  │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │    Response     │
                                    └─────────────────┘
```

## Project Setup

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

## Semantic Kernel Configuration

### Program.cs Setup
```csharp
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Memory;
using Microsoft.SemanticKernel.Connectors.AzureOpenAI;

var builder = WebApplication.CreateBuilder(args);

// Configure Semantic Kernel
builder.Services.AddSingleton(sp =>
{
    var kernelBuilder = Kernel.CreateBuilder();

    // Add Azure OpenAI for chat
    kernelBuilder.AddAzureOpenAIChatCompletion(
        deploymentName: builder.Configuration["AzureOpenAI:ChatDeployment"]!,
        endpoint: builder.Configuration["AzureOpenAI:Endpoint"]!,
        apiKey: builder.Configuration["AzureOpenAI:ApiKey"]!);

    // Add Azure OpenAI for embeddings
    kernelBuilder.AddAzureOpenAITextEmbeddingGeneration(
        deploymentName: builder.Configuration["AzureOpenAI:EmbeddingDeployment"]!,
        endpoint: builder.Configuration["AzureOpenAI:Endpoint"]!,
        apiKey: builder.Configuration["AzureOpenAI:ApiKey"]!);

    return kernelBuilder.Build();
});

// Configure Vector Store (choose one)
builder.Services.AddSingleton<ISemanticTextMemory>(sp =>
{
    var kernel = sp.GetRequiredService<Kernel>();
    var embeddingGenerator = kernel.GetRequiredService<ITextEmbeddingGenerationService>();

    // Azure AI Search
    var memoryBuilder = new MemoryBuilder()
        .WithAzureAISearchMemoryStore(
            builder.Configuration["AzureSearch:Endpoint"]!,
            builder.Configuration["AzureSearch:ApiKey"]!)
        .WithTextEmbeddingGeneration(embeddingGenerator);

    return memoryBuilder.Build();
});

// Register RAG service
builder.Services.AddScoped<IRagService, RagService>();

var app = builder.Build();
```

### appsettings.json
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
  "Rag": {
    "ChunkSize": 500,
    "ChunkOverlap": 100,
    "TopK": 5,
    "MinRelevanceScore": 0.7
  }
}
```

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
    Task<IEnumerable<MemoryQueryResult>> SearchAsync(string query, string collection, int limit = 5, CancellationToken ct = default);
}

public class RagService : IRagService
{
    private readonly Kernel _kernel;
    private readonly ISemanticTextMemory _memory;
    private readonly ILogger<RagService> _logger;
    private readonly RagSettings _settings;

    public RagService(
        Kernel kernel,
        ISemanticTextMemory memory,
        IOptions<RagSettings> settings,
        ILogger<RagService> logger)
    {
        _kernel = kernel;
        _memory = memory;
        _settings = settings.Value;
        _logger = logger;
    }

    public async Task<string> AskAsync(string question, string collection, CancellationToken ct = default)
    {
        _logger.LogInformation("RAG query: {Question}", question);

        // 1. Search for relevant documents
        var searchResults = await SearchAsync(question, collection, _settings.TopK, ct);
        var relevantChunks = searchResults.ToList();

        if (!relevantChunks.Any())
        {
            return "I don't have enough information to answer that question.";
        }

        // 2. Build context from relevant chunks
        var context = BuildContext(relevantChunks);

        // 3. Generate response with LLM
        var response = await GenerateResponseAsync(question, context, ct);

        _logger.LogInformation("RAG response generated with {ChunkCount} context chunks", relevantChunks.Count);

        return response;
    }

    public async Task IngestDocumentAsync(string documentPath, string collection, CancellationToken ct = default)
    {
        _logger.LogInformation("Ingesting document: {Path}", documentPath);

        // 1. Read document content
        var content = await File.ReadAllTextAsync(documentPath, ct);

        // 2. Chunk the content
        var chunks = ChunkText(content, _settings.ChunkSize, _settings.ChunkOverlap);

        // 3. Store each chunk with embedding
        var documentId = Path.GetFileNameWithoutExtension(documentPath);
        var tasks = chunks.Select((chunk, index) =>
            _memory.SaveInformationAsync(
                collection: collection,
                text: chunk,
                id: $"{documentId}_{index}",
                description: $"Chunk {index} from {documentPath}",
                cancellationToken: ct));

        await Task.WhenAll(tasks);

        _logger.LogInformation("Ingested {ChunkCount} chunks from {Path}", chunks.Count, documentPath);
    }

    public async Task<IEnumerable<MemoryQueryResult>> SearchAsync(
        string query,
        string collection,
        int limit = 5,
        CancellationToken ct = default)
    {
        var results = new List<MemoryQueryResult>();

        await foreach (var result in _memory.SearchAsync(
            collection: collection,
            query: query,
            limit: limit,
            minRelevanceScore: _settings.MinRelevanceScore,
            cancellationToken: ct))
        {
            results.Add(result);
        }

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

                // Start new chunk with overlap
                currentChunk.Clear();
                while (overlapBuffer.Count > 0 && currentChunk.Length < overlap)
                {
                    currentChunk.Append(overlapBuffer.Dequeue()).Append(". ");
                }
            }

            currentChunk.Append(sentence).Append(". ");
            overlapBuffer.Enqueue(sentence);

            // Keep overlap buffer size manageable
            while (overlapBuffer.Count > 3)
                overlapBuffer.Dequeue();
        }

        if (currentChunk.Length > 0)
            chunks.Add(currentChunk.ToString().Trim());

        return chunks;
    }

    private static string BuildContext(IEnumerable<MemoryQueryResult> results)
    {
        var sb = new StringBuilder();
        sb.AppendLine("Relevant information:");
        sb.AppendLine();

        foreach (var result in results)
        {
            sb.AppendLine($"[Source: {result.Metadata.Description}]");
            sb.AppendLine(result.Metadata.Text);
            sb.AppendLine();
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

## API Endpoint

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
        AskRequest request,
        IRagService ragService,
        CancellationToken ct)
    {
        var answer = await ragService.AskAsync(request.Question, request.Collection, ct);
        return Results.Ok(new AskResponse(answer));
    }

    private static async Task<IResult> IngestDocument(
        IngestRequest request,
        IRagService ragService,
        CancellationToken ct)
    {
        await ragService.IngestDocumentAsync(request.DocumentPath, request.Collection, ct);
        return Results.NoContent();
    }

    private static async Task<IResult> SearchDocuments(
        SearchRequest request,
        IRagService ragService,
        CancellationToken ct)
    {
        var results = await ragService.SearchAsync(request.Query, request.Collection, request.Limit, ct);
        return Results.Ok(new SearchResponse(results.Select(r => new SearchResult(
            r.Metadata.Id,
            r.Metadata.Text,
            r.Relevance))));
    }
}

public record AskRequest(string Question, string Collection);
public record AskResponse(string Answer);
public record IngestRequest(string DocumentPath, string Collection);
public record SearchRequest(string Query, string Collection, int Limit = 5);
public record SearchResponse(IEnumerable<SearchResult> Results);
public record SearchResult(string Id, string Text, double Relevance);
```

## Vector Store Options

### Azure AI Search
```csharp
var memoryBuilder = new MemoryBuilder()
    .WithAzureAISearchMemoryStore(endpoint, apiKey)
    .WithTextEmbeddingGeneration(embeddingService);
```

### Qdrant
```csharp
var memoryBuilder = new MemoryBuilder()
    .WithQdrantMemoryStore("http://localhost:6333", 1536)
    .WithTextEmbeddingGeneration(embeddingService);
```

### PostgreSQL with pgvector
```csharp
var memoryBuilder = new MemoryBuilder()
    .WithPostgresMemoryStore(connectionString, 1536, "embeddings")
    .WithTextEmbeddingGeneration(embeddingService);
```

### SQL Server (Custom)
```csharp
// SQL Server doesn't have native vector support
// Use custom implementation or Azure SQL with vector support preview
```

## Federal Compliance Considerations

### Data Classification
```csharp
public class FederalRagService : RagService
{
    public override async Task IngestDocumentAsync(string documentPath, string collection, CancellationToken ct)
    {
        // Validate document classification
        var classification = await ValidateClassificationAsync(documentPath);

        if (classification == DataClassification.Classified)
        {
            throw new InvalidOperationException("Classified documents cannot be processed by RAG system");
        }

        if (classification == DataClassification.CUI)
        {
            // Apply CUI handling requirements
            collection = $"cui_{collection}";
            _logger.LogWarning("Processing CUI document: {Path}", documentPath);
        }

        await base.IngestDocumentAsync(documentPath, collection, ct);

        // Log for audit
        await _auditService.LogDocumentIngestionAsync(documentPath, classification);
    }
}

public enum DataClassification
{
    Unclassified,
    CUI,        // Controlled Unclassified Information
    Classified  // Cannot process
}
```

### Air-Gapped Deployment
```csharp
// For disconnected environments, use local models
kernelBuilder.AddOllamaChatCompletion(
    modelId: "llama3",
    endpoint: new Uri("http://localhost:11434"));

kernelBuilder.AddOllamaTextEmbeddingGeneration(
    modelId: "nomic-embed-text",
    endpoint: new Uri("http://localhost:11434"));
```

### Audit Logging
```csharp
public class AuditedRagService : IRagService
{
    private readonly IRagService _inner;
    private readonly IAuditLogger _audit;

    public async Task<string> AskAsync(string question, string collection, CancellationToken ct)
    {
        await _audit.LogAsync(new RagQueryEvent
        {
            Question = question,
            Collection = collection,
            UserId = _currentUser.Id,
            Timestamp = DateTime.UtcNow
        });

        var response = await _inner.AskAsync(question, collection, ct);

        await _audit.LogAsync(new RagResponseEvent
        {
            QuestionHash = ComputeHash(question),
            ResponseLength = response.Length,
            Timestamp = DateTime.UtcNow
        });

        return response;
    }
}
```

## Output Format

```markdown
## RAG Implementation: [Project Name]

**Vector Store**: [Azure AI Search | Qdrant | PostgreSQL]
**LLM Provider**: [Azure OpenAI | OpenAI | Local]
**Embedding Model**: [text-embedding-ada-002 | text-embedding-3-small]

### Configuration

| Setting | Value |
|---------|-------|
| Chunk Size | 500 tokens |
| Chunk Overlap | 100 tokens |
| Top K Results | 5 |
| Min Relevance | 0.7 |

### Collections

| Collection | Documents | Purpose |
|------------|-----------|---------|
| policies | 50 | Company policies |
| procedures | 120 | SOPs |
| training | 30 | Training materials |

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/rag/ask | Question answering |
| POST | /api/rag/ingest | Document ingestion |
| POST | /api/rag/search | Similarity search |

### Security

- Authentication: [JWT | Azure AD]
- Authorization: [Policy-based]
- Data Classification: [Handled | N/A]
- Audit Logging: [Enabled | Disabled]
```

## References

- `references/semantic-kernel-setup.md` - Semantic Kernel configuration
- `references/embedding-models.md` - Embedding model comparison
- `references/vector-store-options.md` - Vector database options
- `references/rag-plugin-templates.md` - Semantic Kernel plugins
- `references/federal-ai-compliance.md` - Federal compliance requirements
