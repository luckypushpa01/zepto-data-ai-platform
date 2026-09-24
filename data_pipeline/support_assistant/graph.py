import os
from typing import TypedDict

import chromadb
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, END

from .models import AskResponse
from .prompt import STRUCTURED_PROMPT


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")
COLLECTION_NAME = "zepto_policies"
MODEL_NAME = "all-MiniLM-L6-v2"


class GraphState(TypedDict, total=False):
    query: str
    intent: str
    answer: str
    sources: list[str]
    confidence: float


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


def classify_intent(state: GraphState):
    query = state["query"].lower()

    if any(keyword in query for keyword in POLICY_KEYWORDS):
        intent = "policy_question"
    else:
        intent = "general_question"

    return {"intent": intent}


def retrieve_and_answer(state: GraphState):
    model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(name=COLLECTION_NAME)

    query_embedding = model.encode(
        [state["query"]],
        normalize_embeddings=True,
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3,
    )

    documents = results["documents"][0]
    ids = results["ids"][0]

    top_chunk = documents[0]
    snippet = top_chunk[:200]

    mock_llm = os.getenv("MOCK_LLM", "1") != "0"

    if mock_llm:
        answer = f"Based on the retrieved context: {snippet}"
    else:
        answer = (
            STRUCTURED_PROMPT.format(
                context="\n\n".join(documents),
                query=state["query"],
            )
        )

    return {
        "answer": answer,
        "sources": ids,
        "confidence": 1.0,
    }


def direct_answer(state: GraphState):
    return {
        "answer": "I can only answer questions about Zepto policies right now.",
        "sources": [],
        "confidence": 1.0,
    }


def route_intent(state: GraphState):
    if state["intent"] == "policy_question":
        return "retrieve_and_answer"
    return "direct_answer"


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("classify_intent", classify_intent)
    graph.add_node("retrieve_and_answer", retrieve_and_answer)
    graph.add_node("direct_answer", direct_answer)

    graph.set_entry_point("classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        route_intent,
        {
            "retrieve_and_answer": "retrieve_and_answer",
            "direct_answer": "direct_answer",
        },
    )

    graph.add_edge("retrieve_and_answer", END)
    graph.add_edge("direct_answer", END)

    return graph.compile()


def answer_query(query: str) -> AskResponse:
    app = build_graph()

    result = app.invoke({"query": query})

    return AskResponse(
        answer=result["answer"],
        sources=result.get("sources", []),
        confidence=result.get("confidence", 1.0),
    )
