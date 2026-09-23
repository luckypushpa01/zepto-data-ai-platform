import json
import os
from pathlib import Path
from typing import Literal, TypedDict

import chromadb
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field, ValidationError
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / "chroma_db"

MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "zepto_policy"

MOCK_LLM = os.getenv("MOCK_LLM", "1") != "0"


# -------------------------------------------------------------------
# Response schema
# -------------------------------------------------------------------

class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: float = Field(ge=0.0, le=1.0)


# -------------------------------------------------------------------
# LangGraph state
# -------------------------------------------------------------------

class GraphState(TypedDict, total=False):
    query: str
    intent: Literal["policy_question", "general_question"]
    retrieved_chunks: list[dict]
    answer: str
    sources: list[str]
    confidence: float


# -------------------------------------------------------------------
# Structured prompt
# -------------------------------------------------------------------

SUPPORT_PROMPT = """
ROLE:
You are a Zepto customer-support assistant.

CONTEXT:
Use only the retrieved Zepto policy context provided below.

TASK:
Answer the customer's question using the retrieved policy context.

FORMAT:
Return valid JSON with exactly these fields:
{
  "answer": "string",
  "sources": ["chunk_id"],
  "confidence": 0.0
}

LENGTH:
Keep the answer concise and under 80 words.

NEGATIVE CONSTRAINT:
Do not invent, assume, or use information that is not supported by the retrieved context.
If the context does not answer the question, clearly say that the available policy context does not provide the answer.

FEW-SHOT EXAMPLE:
User: What is the standard delivery fee for orders below INR 149?
Context: Standard delivery is free on orders over INR 149; orders below this threshold incur a flat INR 25 delivery fee.
Assistant:
{
  "answer": "Orders below INR 149 incur a flat INR 25 standard delivery fee.",
  "sources": ["doc_01_chunk_01"],
  "confidence": 0.98
}

CUSTOMER QUESTION:
{query}

RETRIEVED CONTEXT:
{context}
"""


# -------------------------------------------------------------------
# Local embedding model
# -------------------------------------------------------------------

print(f"Loading embedding model: {MODEL_NAME}")
embedding_model = SentenceTransformer(MODEL_NAME)


# -------------------------------------------------------------------
# ChromaDB
# -------------------------------------------------------------------

chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"},
)


def load_documents() -> list[dict]:
    documents = []

    for path in sorted(DOCS_DIR.glob("doc_*.txt")):
        text = path.read_text(encoding="utf-8").strip()

        if not text:
            continue

        doc_number = path.stem
        chunk_id = f"{doc_number}_chunk_01"

        documents.append(
            {
                "id": chunk_id,
                "document": text,
                "metadata": {
                    "source": doc_number,
                    "chunk": 1,
                },
            }
        )

    return documents


def ingest_documents() -> None:
    documents = load_documents()

    if len(documents) != 8:
        raise RuntimeError(
            f"Expected 8 corpus documents, found {len(documents)}."
        )

    existing_count = collection.count()

    if existing_count >= 8:
        print(f"ChromaDB already contains {existing_count} chunks.")
        return

    texts = [item["document"] for item in documents]
    embeddings = embedding_model.encode(
        texts,
        normalize_embeddings=True,
    ).tolist()

    collection.upsert(
        ids=[item["id"] for item in documents],
        documents=texts,
        embeddings=embeddings,
        metadatas=[item["metadata"] for item in documents],
    )

    print(f"Indexed {len(documents)} chunks into ChromaDB.")


ingest_documents()


# -------------------------------------------------------------------
# Retrieval
# -------------------------------------------------------------------

def retrieve_chunks(query: str, top_k: int = 3) -> list[dict]:
    query_embedding = embedding_model.encode(
        [query],
        normalize_embeddings=True,
    )[0].tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for index, chunk_id in enumerate(ids):
        chunks.append(
            {
                "id": chunk_id,
                "document": documents[index],
                "metadata": metadatas[index],
                "distance": distances[index],
            }
        )

    return chunks


# -------------------------------------------------------------------
# Optional real LLM helper
# -------------------------------------------------------------------

def get_real_llm():
    from langchain_groq import ChatGroq

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "MOCK_LLM=0 requires GROQ_API_KEY to be set."
        )

    return ChatGroq(
        model=os.getenv(
            "GROQ_MODEL",
            "llama-3.1-8b-instant",
        ),
        temperature=0,
        api_key=api_key,
    )


def call_real_llm_with_validation(
    prompt: str,
    fallback_sources: list[str],
) -> AnswerResponse:
    llm = get_real_llm()

    corrective_prompt = prompt

    for attempt in range(3):
        raw = llm.invoke(corrective_prompt).content

        try:
            if isinstance(raw, list):
                raw = "".join(
                    item.get("text", "")
                    if isinstance(item, dict)
                    else str(item)
                    for item in raw
                )

            parsed = json.loads(raw)

            response = AnswerResponse.model_validate(parsed)

            return response

        except (json.JSONDecodeError, ValidationError, TypeError) as exc:
            corrective_prompt = (
                prompt
                + "\n\nCORRECTION:\n"
                "Your previous response failed schema validation. "
                "Return ONLY valid JSON with fields "
                '"answer", "sources", and "confidence". '
                f"Validation error: {exc}"
            )

    return AnswerResponse(
        answer="ERROR: The language model failed response validation.",
        sources=fallback_sources,
        confidence=0.0,
    )


# -------------------------------------------------------------------
# LangGraph nodes
# -------------------------------------------------------------------

POLICY_KEYWORDS = [
    "delivery",
    "return",
    "refund",
    "membership",
    "tracking",
    "cancel",
    "gift card",
    "support hours",
]


def classify_intent(state: GraphState) -> GraphState:
    query = state["query"]

    if MOCK_LLM:
        query_lower = query.lower()

        is_policy = any(
            keyword in query_lower
            for keyword in POLICY_KEYWORDS
        )

        intent = (
            "policy_question"
            if is_policy
            else "general_question"
        )

        return {
            **state,
            "intent": intent,
        }

    llm = get_real_llm()

    prompt = f"""
Classify this customer query as exactly one of:
policy_question
general_question

Query:
{query}

Return only one label.
"""

    raw = llm.invoke(prompt).content.strip().lower()

    if "policy_question" in raw:
        intent = "policy_question"
    else:
        intent = "general_question"

    return {
        **state,
        "intent": intent,
    }


def retrieve_and_answer(state: GraphState) -> GraphState:
    query = state["query"]

    chunks = retrieve_chunks(query, top_k=3)

    source_ids = [chunk["id"] for chunk in chunks]

    if not chunks:
        return {
            **state,
            "retrieved_chunks": [],
            "answer": "No relevant policy context was retrieved.",
            "sources": [],
            "confidence": 0.0,
        }

    if MOCK_LLM:
        top_chunk_snippet = chunks[0]["document"][:200]

        return {
            **state,
            "retrieved_chunks": chunks,
            "answer": (
                "Based on the retrieved context: "
                f"{top_chunk_snippet}"
            ),
            "sources": source_ids,
            "confidence": 0.90,
        }

    context = "\n\n".join(
        f"[{chunk['id']}]\n{chunk['document']}"
        for chunk in chunks
    )

    prompt = SUPPORT_PROMPT.format(
        query=query,
        context=context,
    )

    response = call_real_llm_with_validation(
        prompt,
        fallback_sources=source_ids,
    )

    return {
        **state,
        "retrieved_chunks": chunks,
        "answer": response.answer,
        "sources": response.sources,
        "confidence": response.confidence,
    }


def direct_answer(state: GraphState) -> GraphState:
    if MOCK_LLM:
        return {
            **state,
            "answer": (
                "I can only answer questions about Zepto policies right now."
            ),
            "sources": [],
            "confidence": 1.0,
        }

    query = state["query"]

    prompt = f"""
ROLE:
You are a Zepto customer-support assistant.

TASK:
Answer the customer's general question.

FORMAT:
Return valid JSON with exactly:
{{
  "answer": "string",
  "sources": [],
  "confidence": 0.0
}}

LENGTH:
Keep the answer under 80 words.

NEGATIVE CONSTRAINT:
Do not invent Zepto policy information.

FEW-SHOT EXAMPLE:
User: What is the capital of France?
Assistant:
{{
  "answer": "I can only answer questions about Zepto policies right now.",
  "sources": [],
  "confidence": 1.0
}}

CUSTOMER QUESTION:
{query}
"""

    response = call_real_llm_with_validation(
        prompt,
        fallback_sources=[],
    )

    return {
        **state,
        "answer": response.answer,
        "sources": response.sources,
        "confidence": response.confidence,
    }


def route_after_classification(state: GraphState) -> str:
    if state["intent"] == "policy_question":
        return "retrieve_and_answer"

    return "direct_answer"


# -------------------------------------------------------------------
# Build LangGraph StateGraph
# -------------------------------------------------------------------

graph_builder = StateGraph(GraphState)

graph_builder.add_node(
    "classify_intent",
    classify_intent,
)

graph_builder.add_node(
    "retrieve_and_answer",
    retrieve_and_answer,
)

graph_builder.add_node(
    "direct_answer",
    direct_answer,
)

graph_builder.add_edge(
    START,
    "classify_intent",
)

graph_builder.add_conditional_edges(
    "classify_intent",
    route_after_classification,
    {
        "retrieve_and_answer": "retrieve_and_answer",
        "direct_answer": "direct_answer",
    },
)

graph_builder.add_edge(
    "retrieve_and_answer",
    END,
)

graph_builder.add_edge(
    "direct_answer",
    END,
)

graph = graph_builder.compile()


# -------------------------------------------------------------------
# Public application function
# -------------------------------------------------------------------

def answer_query(query: str) -> AnswerResponse:
    result = graph.invoke(
        {
            "query": query,
        }
    )

    response = AnswerResponse(
        answer=result["answer"],
        sources=result.get("sources", []),
        confidence=result.get("confidence", 0.0),
    )

    return response