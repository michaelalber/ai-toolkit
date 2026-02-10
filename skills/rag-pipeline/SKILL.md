---
name: rag-pipeline
description: Scaffold RAG pipelines with Ollama or cloud embeddings. Use when building retrieval-augmented generation systems with local or cloud LLMs, vector stores, and document processing.
---

# RAG Pipeline Scaffold

> "The quality of your RAG system is bounded by the quality of your retrieval, not the quality of your generation model."
> -- Jerry Liu, creator of LlamaIndex

## Core Philosophy

This skill scaffolds end-to-end Retrieval-Augmented Generation pipelines: document ingestion, chunking, embedding, indexing, retrieval, generation, and evaluation. Every design decision is grounded in **retrieval quality** and **measurable relevance**.

**Non-Negotiable Constraints:**
1. Retrieval quality MUST be measured before generation is tuned -- garbage in, garbage out
2. Chunk size and overlap MUST be chosen deliberately based on corpus type and embedding model context window
3. Every pipeline MUST include an evaluation step with representative queries before deployment
4. Embedding model selection MUST account for dimensionality, speed, and domain fit
5. Document preprocessing MUST be validated -- never embed raw, unparsed content with formatting artifacts

## Domain Principles Table

| # | Principle | Description | Priority |
|---|-----------|-------------|----------|
| 1 | **Retrieval Precision** | Retrieved chunks must be relevant to the query. Measure precision@k and MRR before tuning generation. Irrelevant context degrades output quality more than no context at all. | Critical |
| 2 | **Chunk Coherence** | Each chunk must be a self-contained unit of meaning. A chunk that starts mid-sentence or splits a code block is worse than a slightly larger chunk that preserves boundaries. | Critical |
| 3 | **Embedding Quality** | The embedding model determines the ceiling of retrieval performance. Evaluate embeddings on domain-specific queries, not just general benchmarks. Local models (sentence-transformers, Ollama) trade quality for privacy and speed. | Critical |
| 4 | **Context Window Awareness** | The total retrieved context plus the prompt must fit within the generation model's context window. Overstuffing degrades quality; understuffing wastes capacity. Calculate token budgets explicitly. | High |
| 5 | **Document Preprocessing** | Raw documents contain noise: headers, footers, page numbers, formatting artifacts, boilerplate. Preprocessing must strip noise while preserving semantic content. Validate by spot-checking chunks. | High |
| 6 | **Metadata Enrichment** | Every chunk should carry metadata: source document, page/section, creation date, document type. Metadata enables filtered retrieval and source attribution in generated answers. | High |
| 7 | **Index Freshness** | Stale indexes produce stale answers. Define an update strategy: full rebuild, incremental upsert, or change-detection based. Document the refresh cadence. | Medium |
| 8 | **Query Transformation** | Raw user queries are often poor retrieval queries. Consider query expansion, HyDE (Hypothetical Document Embeddings), or multi-query retrieval to improve recall. | Medium |
| 9 | **Answer Grounding** | Generated answers MUST cite their source chunks. Hallucinated answers that sound confident but lack grounding are the primary failure mode of RAG systems. | Critical |
| 10 | **Cost Awareness** | Cloud embeddings and LLMs have per-token costs. Local models (Ollama, sentence-transformers) have compute costs. Estimate costs per query and per corpus re-index before committing to a design. | Medium |

## Workflow

### RAG Pipeline Lifecycle

```
+-----------------------------------------------------------------------+
|                      RAG PIPELINE WORKFLOW                             |
|                                                                       |
|  +--------+   +-------+   +-------+   +-------+                      |
|  |1.INGEST|-->|2.CHUNK|-->|3.EMBED|-->|4.INDEX|                      |
|  +--------+   +-------+   +-------+   +-------+                      |
|       |                                    |                          |
|       |                                    v                          |
|       |                              +----------+    +----------+    |
|       |                              |5.RETRIEVE|--->|6.GENERATE|    |
|       |                              +----------+    +----------+    |
|       |                                                   |          |
|       |                                                   v          |
|       |                                             +----------+     |
|       |                                             |7.EVALUATE|     |
|       |                                             +----------+     |
|       |                                                   |          |
|       +---------------------------------------------------+          |
|                         (iterate if needed)                           |
+-----------------------------------------------------------------------+
```

### Pre-Flight Checklist

Before starting a RAG pipeline scaffold:

```
+-----------------------------------------------+
| RAG Pre-Flight Checklist                      |
+-----------------------------------------------+
| [ ] Corpus identified (type, size, format)    |
| [ ] Sample documents available for testing    |
| [ ] Hardware assessed (GPU/CPU, RAM, disk)    |
| [ ] Embedding model selected (local/cloud)    |
| [ ] Vector store selected                     |
| [ ] Generation model selected (Ollama/cloud)  |
| [ ] Representative test queries drafted       |
| [ ] Success criteria defined (precision@k)    |
+-----------------------------------------------+
```

### Step 1: INGEST -- Document Loading

Load documents from source and validate content extraction.

```python
# Example: Multi-format document ingestion
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    TextLoader,
    DirectoryLoader,
)

def ingest_documents(source_dir: str) -> list:
    """Load documents from a directory, handling multiple formats."""
    loaders = {
        "*.pdf": PyPDFLoader,
        "*.md": UnstructuredMarkdownLoader,
        "*.txt": TextLoader,
    }

    all_docs = []
    for glob_pattern, loader_cls in loaders.items():
        loader = DirectoryLoader(
            source_dir,
            glob=glob_pattern,
            loader_cls=loader_cls,
            show_progress=True,
        )
        docs = loader.load()
        all_docs.extend(docs)

    print(f"Loaded {len(all_docs)} documents from {source_dir}")
    return all_docs
```

**Validation**: After ingestion, spot-check 3-5 documents to confirm text extraction preserved semantic content without artifacts.

### Step 2: CHUNK -- Text Splitting

Choose a chunking strategy based on corpus type. See [Chunking Strategies Reference](references/chunking-strategies.md) for detailed implementations.

**Chunking Strategy Decision Tree:**

```
What is the corpus type?
|
+-- Structured documents (Markdown, HTML)?
|   --> Recursive character splitting with Markdown/HTML separators
|
+-- Dense prose (PDF, articles, books)?
|   --> Semantic chunking with sentence-transformers
|   --> Fallback: Recursive character splitting (1000 chars, 200 overlap)
|
+-- Source code?
|   --> Language-aware splitting (LangChain CodeTextSplitter)
|
+-- Mixed content?
|   --> Route by document type, apply type-specific strategy
|
+-- Short documents (< 1 page each)?
|   --> Consider embedding whole documents without splitting
```

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_documents(docs: list, chunk_size: int = 1000, chunk_overlap: int = 200) -> list:
    """Split documents into chunks with overlap."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(docs)
    print(f"Split {len(docs)} documents into {len(chunks)} chunks")
    print(f"Avg chunk size: {sum(len(c.page_content) for c in chunks) / len(chunks):.0f} chars")
    return chunks
```

### Step 3: EMBED -- Generate Embeddings

Select an embedding model based on privacy, cost, and quality requirements.

**Embedding Model Decision Tree:**

```
What are the constraints?
|
+-- Data must stay local (privacy/air-gapped)?
|   |
|   +-- GPU available?
|   |   --> sentence-transformers (all-MiniLM-L6-v2, all-mpnet-base-v2)
|   |   --> Ollama (nomic-embed-text, mxbai-embed-large)
|   |
|   +-- CPU only?
|       --> sentence-transformers (all-MiniLM-L6-v2) -- fastest small model
|       --> Ollama (nomic-embed-text) -- good quality/speed tradeoff
|
+-- Cloud is acceptable?
|   |
|   +-- OpenAI budget?
|   |   --> text-embedding-3-small (cost-effective)
|   |   --> text-embedding-3-large (higher quality)
|   |
|   +-- Other providers?
|       --> Cohere embed-v3
|       --> Voyage AI
|
+-- Need multilingual support?
    --> sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
    --> Cohere embed-v3 (multilingual)
```

```python
# Local embeddings with sentence-transformers
from langchain_community.embeddings import HuggingFaceEmbeddings

def get_local_embeddings(model_name: str = "all-MiniLM-L6-v2"):
    """Initialize local embedding model via sentence-transformers."""
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cuda"},  # Use "cpu" if no GPU
        encode_kwargs={"normalize_embeddings": True, "batch_size": 64},
    )


# Local embeddings with Ollama
from langchain_ollama import OllamaEmbeddings

def get_ollama_embeddings(model_name: str = "nomic-embed-text"):
    """Initialize embedding model via Ollama."""
    return OllamaEmbeddings(model=model_name)
```

### Step 4: INDEX -- Store in Vector Database

See [Vector Store Patterns Reference](references/vector-store-patterns.md) for detailed setup.

```python
from langchain_chroma import Chroma

def index_chunks(chunks: list, embeddings, persist_directory: str = "./chroma_db") -> Chroma:
    """Index chunks into ChromaDB vector store."""
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name="rag_collection",
    )
    print(f"Indexed {len(chunks)} chunks into ChromaDB at {persist_directory}")
    return vectorstore
```

### Step 5: RETRIEVE -- Semantic Search

```python
def retrieve(vectorstore, query: str, top_k: int = 5) -> list:
    """Retrieve relevant chunks for a query."""
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k},
    )
    results = retriever.invoke(query)
    print(f"Retrieved {len(results)} chunks for query: '{query[:60]}...'")
    return results
```

### Step 6: GENERATE -- Augmented Generation

```python
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def build_rag_chain(vectorstore, model_name: str = "llama3.1"):
    """Build a RAG chain with Ollama generation."""
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    llm = ChatOllama(model=model_name, temperature=0.1)

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a helpful assistant. Answer the question based ONLY on "
            "the provided context. If the context does not contain enough "
            "information to answer, say so explicitly. Cite the source "
            "document for each claim.\n\n"
            "Context:\n{context}"
        )),
        ("human", "{question}"),
    ])

    def format_docs(docs):
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "unknown")
            formatted.append(f"[{i}] (Source: {source})\n{doc.page_content}")
        return "\n\n".join(formatted)

    chain = (
        {"context": retriever | format_docs, "question": lambda x: x}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain
```

### Step 7: EVALUATE -- Measure Retrieval and Generation Quality

```python
def evaluate_retrieval(vectorstore, test_queries: list[dict], top_k: int = 5) -> dict:
    """Evaluate retrieval quality with labeled test queries.

    Each test query should have:
        {"query": "...", "expected_sources": ["doc1.pdf", "doc2.pdf"]}
    """
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
    results = {"precision_at_k": [], "recall": [], "mrr": []}

    for tq in test_queries:
        retrieved = retriever.invoke(tq["query"])
        retrieved_sources = [d.metadata.get("source", "") for d in retrieved]

        # Precision@k
        relevant = sum(1 for s in retrieved_sources if s in tq["expected_sources"])
        precision = relevant / top_k
        results["precision_at_k"].append(precision)

        # Recall
        found = sum(1 for s in tq["expected_sources"] if s in retrieved_sources)
        recall = found / len(tq["expected_sources"]) if tq["expected_sources"] else 0
        results["recall"].append(recall)

        # MRR (Mean Reciprocal Rank)
        rr = 0.0
        for rank, source in enumerate(retrieved_sources, 1):
            if source in tq["expected_sources"]:
                rr = 1.0 / rank
                break
        results["mrr"].append(rr)

    def compute_avg(vals):
        return sum(vals) / len(vals) if vals else 0

    return {
        "avg_precision_at_k": compute_avg(results["precision_at_k"]),
        "avg_recall": compute_avg(results["recall"]),
        "avg_mrr": compute_avg(results["mrr"]),
        "num_queries": len(test_queries),
    }
```

## State Block Format

Maintain state across conversation turns using this block:

```
<rag-state>
step: [INGEST | CHUNK | EMBED | INDEX | RETRIEVE | GENERATE | EVALUATE]
corpus_type: [pdf | markdown | code | mixed]
chunking_strategy: [fixed | semantic | recursive | sentence]
embedding_model: [model name]
vector_store: [chromadb | faiss | qdrant | pgvector]
last_action: [what was just done]
next_action: [what should happen next]
blockers: [any issues]
</rag-state>
```

**Example:**

```
<rag-state>
step: EVALUATE
corpus_type: pdf
chunking_strategy: recursive
embedding_model: all-MiniLM-L6-v2
vector_store: chromadb
last_action: Built RAG chain with Ollama llama3.1
next_action: Run evaluation with 10 representative test queries
blockers: none
</rag-state>
```

## Output Templates

### Pipeline Scaffold Report

```markdown
## RAG Pipeline Scaffold

**Corpus**: [description, size, format]
**Embedding Model**: [model name, local/cloud, dimensions]
**Vector Store**: [store name, collection, index type]
**Generation Model**: [model name, local/cloud]

### Architecture

| Stage | Component | Configuration |
|-------|-----------|---------------|
| Ingest | [loader] | [formats supported] |
| Chunk | [strategy] | [chunk_size / overlap] |
| Embed | [model] | [dimensions, batch_size] |
| Index | [store] | [collection, distance_metric] |
| Retrieve | [search_type] | [top_k, filters] |
| Generate | [model] | [temperature, max_tokens] |

### Dependencies

\```
pip install langchain langchain-community langchain-chroma
pip install langchain-ollama sentence-transformers
pip install chromadb pypdf pdfplumber
\```

### File Structure

\```
project/
  rag_pipeline/
    __init__.py
    ingest.py        # Document loading
    chunking.py      # Text splitting strategies
    embeddings.py    # Embedding model setup
    vectorstore.py   # Index management
    retrieval.py     # Search and retrieval
    generation.py    # RAG chain construction
    evaluation.py    # Retrieval and generation metrics
  tests/
    test_chunking.py
    test_retrieval.py
    test_pipeline.py
  data/
    documents/       # Source documents
  chroma_db/         # Persisted vector store
  requirements.txt
\```
```

### Evaluation Report

```markdown
## RAG Evaluation Report

**Date**: [date]
**Corpus**: [description]
**Embedding Model**: [model]
**Vector Store**: [store]
**Generation Model**: [model]

### Retrieval Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Precision@5 | [X.XX] | >= 0.70 | PASS/FAIL |
| Recall | [X.XX] | >= 0.80 | PASS/FAIL |
| MRR | [X.XX] | >= 0.60 | PASS/FAIL |

### Generation Quality

| Query | Retrieved Context Relevant? | Answer Grounded? | Answer Correct? |
|-------|----------------------------|------------------|-----------------|
| [q1]  | Yes/No                     | Yes/No           | Yes/No          |

### Failure Analysis

| Query | Issue | Root Cause | Recommended Fix |
|-------|-------|------------|-----------------|
| [q]   | [issue] | [cause] | [fix] |

### Recommendations

- [Recommendation 1]
- [Recommendation 2]
```

## AI Discipline Rules

### CRITICAL: Always Evaluate Retrieval Before Generation

Before tuning generation prompts or model parameters:

```
STOP! Verify:
1. Retrieval has been tested with representative queries
2. Precision@k meets the target threshold (>= 0.70)
3. Retrieved chunks are actually relevant (spot-check manually)
4. No systemic retrieval failures (e.g., all queries returning same chunks)

If retrieval quality is poor, fix chunking/embedding FIRST.
Tuning generation on bad retrieval is wasted effort.
```

```python
# WRONG: Jump straight to generation tuning
chain = build_rag_chain(vectorstore, model_name="llama3.1")
# "Hmm, answers are bad, let me try a better prompt..."

# RIGHT: Evaluate retrieval first
retrieval_results = evaluate_retrieval(vectorstore, test_queries)
print(f"Precision@5: {retrieval_results['avg_precision_at_k']:.2f}")
if retrieval_results["avg_precision_at_k"] < 0.70:
    print("STOP: Fix retrieval before tuning generation")
    # Adjust chunk_size, embedding model, or query strategy
```

### CRITICAL: Chunk Size Must Match Embedding Model Context

Every embedding model has a maximum token limit. Chunks that exceed it are silently truncated, destroying semantic meaning.

```
MANDATORY before embedding:
1. Know the embedding model's max token limit
2. Verify that chunk_size (in tokens) is within the limit
3. Account for the difference between characters and tokens (~4 chars/token for English)
4. Leave a 10% margin below the limit

Common limits:
  all-MiniLM-L6-v2:     256 tokens  (~1024 chars)
  all-mpnet-base-v2:    384 tokens  (~1536 chars)
  nomic-embed-text:     8192 tokens (~32768 chars)
  text-embedding-3-small: 8191 tokens
```

```python
# WRONG: 2000-char chunks with a 256-token model
splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  # 256 token limit!
# Chunks will be truncated silently, losing meaning

# RIGHT: Match chunk size to model capacity
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MAX_TOKENS = 256
CHARS_PER_TOKEN = 4
SAFETY_MARGIN = 0.9

chunk_size = int(MAX_TOKENS * CHARS_PER_TOKEN * SAFETY_MARGIN)  # ~920 chars
splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=int(chunk_size * 0.2),
)
```

### CRITICAL: Never Skip Document Preprocessing

Raw documents contain noise that degrades retrieval quality. Every document type needs preprocessing.

```
MANDATORY before chunking:
1. PDF: Strip headers, footers, page numbers, watermarks
2. Markdown: Preserve heading structure for metadata
3. HTML: Remove navigation, ads, boilerplate; keep semantic content
4. Code: Preserve indentation and block structure
5. All types: Normalize whitespace, fix encoding issues
```

```python
import re

def preprocess_text(text: str) -> str:
    """Clean raw document text before chunking."""
    # Normalize whitespace
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    # Remove page numbers and headers/footers (common PDF artifacts)
    text = re.sub(r"\n\s*Page \d+ of \d+\s*\n", "\n", text)
    text = re.sub(r"\n\s*-\s*\d+\s*-\s*\n", "\n", text)

    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
```

### CRITICAL: Test With Representative Queries Before Deployment

A RAG pipeline is only as good as its performance on real queries. Never deploy without testing.

```
MANDATORY before deployment:
1. Draft at least 10 representative queries spanning different topics in the corpus
2. For each query, identify the expected source documents
3. Run retrieval evaluation and verify precision@k >= 0.70
4. Run 5 end-to-end queries and verify answers are grounded in retrieved context
5. Test at least 2 adversarial queries (questions the corpus cannot answer)

If the pipeline cannot correctly say "I don't know" for out-of-scope queries,
it WILL hallucinate in production.
```

```python
# Test queries with expected results
test_queries = [
    {
        "query": "How do I configure the database connection?",
        "expected_sources": ["docs/configuration.md", "docs/database-setup.md"],
    },
    {
        "query": "What are the API rate limits?",
        "expected_sources": ["docs/api-reference.md"],
    },
    # Adversarial: corpus does not cover this topic
    {
        "query": "What is the company's stock price?",
        "expected_sources": [],  # Should retrieve nothing relevant
    },
]

results = evaluate_retrieval(vectorstore, test_queries)
print(f"Avg Precision@5: {results['avg_precision_at_k']:.2f}")
print(f"Avg Recall: {results['avg_recall']:.2f}")
print(f"Avg MRR: {results['avg_mrr']:.2f}")
```

## Anti-Patterns Table

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|-------------|------------------|
| **Embedding entire documents without chunking** | Large documents exceed embedding model context; similarity search returns irrelevant noise | Chunk documents into coherent segments sized for the embedding model |
| **One chunk size for all document types** | Code needs different boundaries than prose; PDFs differ from Markdown | Use document-type-specific chunking strategies |
| **Skipping retrieval evaluation** | Generation quality is bounded by retrieval quality; bad retrieval means bad answers regardless of LLM | Evaluate precision@k and recall before tuning generation |
| **Stuffing all retrieved chunks into context** | Overfilling the context window dilutes relevant information and increases latency/cost | Use top_k judiciously; rerank if needed; respect token budgets |
| **No metadata on chunks** | Cannot filter by source, date, or type; cannot provide source attribution in answers | Attach source, page, section, and date metadata to every chunk |
| **Using cosine similarity without normalization** | Unnormalized embeddings produce inconsistent similarity scores | Normalize embeddings at index time; use `normalize_embeddings=True` |
| **Hardcoding embedding model without benchmarking** | Different models have different strengths; what works for English prose may fail for code | Benchmark 2-3 embedding models on domain-specific queries before choosing |
| **No preprocessing of raw documents** | PDF artifacts, HTML boilerplate, and formatting noise degrade embedding quality | Preprocess and validate document content before chunking |

## Error Recovery

### Low Retrieval Precision

```
Problem: Precision@k is below 0.50 -- retrieved chunks are not relevant
Actions:
1. Inspect retrieved chunks manually for 3-5 queries
2. Check if chunks are too large (splitting semantic units across chunks)
3. Check if chunks are too small (losing context needed for matching)
4. Try a different embedding model (upgrade from MiniLM to mpnet or nomic)
5. Add metadata filtering to narrow retrieval scope
6. Consider query transformation (HyDE, multi-query)
7. Re-evaluate after each change; do not change multiple variables at once
```

### Embedding Dimension Mismatch

```
Problem: Vector store rejects embeddings or returns garbage results
Actions:
1. Verify the embedding model's output dimension matches the index configuration
2. If you changed embedding models, you MUST rebuild the entire index
3. Common dimensions: MiniLM=384, mpnet=768, nomic-embed-text=768, OpenAI=1536/3072
4. Drop and recreate the collection with the correct dimension
5. Re-embed and re-index all documents
```

### Out of Memory During Embedding

```
Problem: Embedding large corpus causes OOM on GPU or RAM exhaustion
Actions:
1. Reduce batch_size in embedding model configuration (e.g., 64 -> 16)
2. Process documents in batches, persisting to vector store incrementally
3. Use CPU embeddings if GPU VRAM is insufficient (slower but stable)
4. For very large corpora (>100k documents), consider cloud embedding APIs
5. Monitor memory usage: nvidia-smi for GPU, htop for RAM
```

### Generation Hallucination

```
Problem: Generated answers contain information not present in retrieved context
Actions:
1. Verify the system prompt explicitly instructs "answer ONLY from context"
2. Check if retrieved chunks actually contain the needed information (retrieval issue)
3. Lower generation temperature (0.1 or lower for factual tasks)
4. Add explicit grounding instructions: "If context is insufficient, say so"
5. Implement post-generation verification: check answer claims against source chunks
6. Consider using a structured output format that forces source citation
```

### ChromaDB Persistence Issues

```
Problem: Vector store data lost between sessions or corrupted
Actions:
1. Verify persist_directory is set and writable
2. Check disk space -- ChromaDB needs space for both data and WAL
3. Ensure the process is not killed during write operations
4. If corrupted, delete the persist_directory and re-index from source documents
5. For production, consider Qdrant or pgvector with proper backup strategies
```

## Integration with Other Skills

### Ollama Model Workflow (`ollama-model-workflow`)

RAG pipelines rely on two Ollama-managed models: an embedding model and a generation model.

**Embedding Model Selection:**
Use the `ollama-model-workflow` skill to select and benchmark embedding models for the RAG pipeline. Key considerations:
- `nomic-embed-text` -- Good general-purpose, 768 dimensions, 8192 token context
- `mxbai-embed-large` -- Higher quality, 1024 dimensions, requires more VRAM
- Always benchmark embedding throughput (documents/sec) alongside quality

**Generation Model Selection:**
Use the `ollama-model-workflow` skill to select the generation model. Key considerations:
- Match `num_ctx` to the expected retrieval context size plus prompt overhead
- Use low temperature (0.1-0.3) for factual RAG tasks
- Benchmark time-to-first-token for interactive RAG applications

```python
# Pull and configure models for RAG via Ollama
import subprocess

def setup_ollama_models():
    """Pull required Ollama models for the RAG pipeline."""
    models = ["nomic-embed-text", "llama3.1:8b-instruct-q5_K_M"]
    for model in models:
        print(f"Pulling {model}...")
        subprocess.run(["ollama", "pull", model], check=True)
    print("All models ready.")
```

### MCP Server Scaffold (`mcp-server-scaffold`)

RAG pipelines are natural backends for MCP server tools. Use the `mcp-server-scaffold` skill to expose the pipeline as MCP tools:

```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("rag-server")

@mcp.tool()
async def search_knowledge_base(query: str, top_k: int = 5, ctx: Context = None) -> str:
    """Search the knowledge base using semantic similarity.

    Returns the top matching document chunks with source attribution.
    """
    if ctx:
        ctx.info(f"RAG search: query='{query}', top_k={top_k}")

    try:
        results = retriever.invoke(query)
        formatted = []
        for i, doc in enumerate(results[:top_k], 1):
            source = doc.metadata.get("source", "unknown")
            formatted.append(f"[{i}] Source: {source}\n{doc.page_content}")
        return "\n\n---\n\n".join(formatted)
    except Exception as e:
        if ctx:
            ctx.error(f"RAG search failed: {e}")
        return f"Error: Search failed - {e}"


@mcp.tool()
async def ask_knowledge_base(question: str, ctx: Context = None) -> str:
    """Ask a question and get an answer grounded in the knowledge base."""
    if ctx:
        ctx.info(f"RAG question: '{question}'")

    try:
        answer = rag_chain.invoke(question)
        return answer
    except Exception as e:
        if ctx:
            ctx.error(f"RAG generation failed: {e}")
        return f"Error: Generation failed - {e}"
```

## Reference Files

- [Chunking Strategies](references/chunking-strategies.md) -- Detailed chunking implementations for every document type
- [Vector Store Patterns](references/vector-store-patterns.md) -- Setup, CRUD operations, and performance comparisons for ChromaDB, FAISS, Qdrant, and pgvector
