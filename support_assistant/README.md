# Zepto Support Assistant

A GenAI-powered customer support assistant for Zepto policies using local embeddings, ChromaDB retrieval, LangGraph orchestration, structured Pydantic responses, and FastAPI.

## Architecture

The application follows this flow:

```text
8 Policy Documents
       ↓
Document Ingestion
       ↓
Chunking
       ↓
Sentence-Transformer Embeddings
(all-MiniLM-L6-v2)
       ↓
ChromaDB
       ↓
User Query
       ↓
LangGraph Intent Classification
       ↓
 ┌───────────────────────┐
 │                       │
Policy Query        General Query
 │                       │
 ↓                       ↓
Top-3 Retrieval     Direct Answer
 │
 ↓
Structured Response
 │
 ↓
FastAPI /ask
```

## Project Structure

```text
support_assistant/
├── docs/
│   ├── doc_01.txt
│   ├── doc_02.txt
│   ├── doc_03.txt
│   ├── doc_04.txt
│   ├── doc_05.txt
│   ├── doc_06.txt
│   ├── doc_07.txt
│   └── doc_08.txt
├── rag.py
├── main.py
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md
```

## Corpus

The assistant uses exactly 8 Zepto policy documents:

1. Delivery Policy
2. Returns & Refunds
3. Membership Tiers
4. Order Tracking
5. Order Cancellation Policy
6. Damaged or Missing Items
7. Gift Cards
8. Customer Support Hours

Each document is loaded from `docs/` and stored as one chunk.

## Embedding and Retrieval

The embedding model is:

```text
all-MiniLM-L6-v2
```

Embeddings are generated locally using Sentence-Transformers.

ChromaDB is used as the vector database with cosine similarity.

For every policy query:

* The user query is embedded using the same embedding model.
* The top 3 most similar chunks are retrieved.
* Retrieved chunk IDs are returned as sources.
* The highest-ranked chunk is used for the deterministic mock response.

The ChromaDB collection is named:

```text
zepto_policy
```

## LangGraph Workflow

The LangGraph workflow is implemented in `rag.py`.

### State

The graph uses a `TypedDict` state containing:

* `query`
* `intent`
* `retrieved_chunks`
* `answer`
* `sources`
* `confidence`

### Nodes

The graph contains three main nodes.

#### `classify_intent`

Classifies the query as either:

```text
policy
general
```

When `MOCK_LLM=1` (the default), classification uses the required keyword heuristic:

```text
delivery
return
refund
membership
tracking
cancel
gift card
support hours
```

When `MOCK_LLM=0`, the optional real LLM branch can be used.

#### `retrieve_and_answer`

For policy queries:

1. Embeds the user query.
2. Retrieves the top 3 ChromaDB chunks.
3. Generates the answer.

In mock mode, the response follows the required deterministic pattern:

```text
Based on the retrieved context: {top_chunk_snippet}
```

The returned sources contain the retrieved chunk IDs.

#### `direct_answer`

For general queries, mock mode returns:

```text
I can only answer questions about Zepto policies right now.
```

The source list is empty.

### Conditional Routing

After `classify_intent`:

```text
policy  → retrieve_and_answer
general → direct_answer
```

Both branches then terminate the graph.

## Structured Response

The response is validated using Pydantic:

```text
answer: string
sources: list[string]
confidence: float
```

The confidence value is constrained to:

```text
0 ≤ confidence ≤ 1
```

In mock mode the output is deterministic.

In real LLM mode, validation failures are retried up to two additional times with a corrective instruction before returning an error response.

## Prompt Design

The structured support prompt follows the required sections:

```text
ROLE
CONTEXT
TASK
FORMAT
LENGTH
```

It also includes:

* A negative constraint to avoid unsupported information.
* A few-shot example showing the expected response behavior.

## Mock LLM Mode

The default configuration is:

```text
MOCK_LLM=1
```

This allows the project to run deterministically without requiring an external LLM API key.

To enable the optional real LLM branch:

```bash
export MOCK_LLM=0
export GROQ_API_KEY="your_api_key"
```

The real LLM model can be configured with:

```bash
export GROQ_MODEL="your_model_name"
```

## FastAPI

The API is implemented in:

```text
main.py
```

The endpoint is:

```text
POST /ask
```

Request format:

```json
{
  "query": "How long does Zepto delivery take?"
}
```

Response format:

```json
{
  "answer": "Based on the retrieved context: ...",
  "sources": [
    "doc_01_chunk_01",
    "doc_08_chunk_01",
    "doc_04_chunk_01"
  ],
  "confidence": 0.9
}
```

## Running Locally

Activate the environment:

```bash
conda activate zepto-support
```

Start the API:

```bash
uvicorn support_assistant.main:app --host 0.0.0.0 --port 7860
```

The API runs on port `7860`.

### Policy Query Test

```bash
curl -X POST http://127.0.0.1:7860/ask \
-H "Content-Type: application/json" \
-d '{"query":"How long does Zepto delivery take?"}'
```

Observed response:

```json
{
  "answer": "Based on the retrieved context: Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer's delivery zone and current order volume. Standard del",
  "sources": [
    "doc_01_chunk_01",
    "doc_08_chunk_01",
    "doc_04_chunk_01"
  ],
  "confidence": 0.9
}
```

### General Query Test

```bash
curl -X POST http://127.0.0.1:7860/ask \
-H "Content-Type: application/json" \
-d '{"query":"What is the capital of France?"}'
```

Observed response:

```json
{
  "answer": "I can only answer questions about Zepto policies right now.",
  "sources": [],
  "confidence": 1.0
}
```

## Docker

A Dockerfile is included for containerized deployment.

The container is configured to run:

```bash
uvicorn support_assistant.main:app --host 0.0.0.0 --port 7860
```

Docker Desktop was not run locally because the development Mac did not have sufficient free disk space. The Dockerfile is included for reproducible container deployment on a system with Docker available.

## Dependencies

The main dependencies include:

```text
fastapi
uvicorn[standard]
pydantic
langgraph
langchain-core
langchain-groq
sentence-transformers==3.0.1
transformers==4.41.2
torch==2.2.2
numpy==1.26.4
scipy==1.13.1
chromadb
```

The pinned ML package versions were selected for compatibility with the local Python 3.12 environment.

## Key Files and Functions

| File               | Purpose                                                                    |
| ------------------ | -------------------------------------------------------------------------- |
| `rag.py`           | RAG pipeline, embeddings, ChromaDB, LangGraph, prompt, response validation |
| `main.py`          | FastAPI application and `/ask` endpoint                                    |
| `docs/`            | 8 source policy documents                                                  |
| `requirements.txt` | Python dependencies                                                        |
| `Dockerfile`       | Container configuration                                                    |
| `.gitignore`       | Excludes Python cache files and local ChromaDB data                        |

Important functions and nodes include:

```text
load_documents()
ingest_documents()
retrieve_chunks()
classify_intent()
retrieve_and_answer()
direct_answer()
route_after_classification()
answer_query()
```
