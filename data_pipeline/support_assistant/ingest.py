from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "zepto_policies"
MODEL_NAME = "all-MiniLM-L6-v2"


def load_documents():
    documents = []
    for path in sorted(DOCS_DIR.glob("doc_*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        documents.append(
            {
                "id": path.stem,
                "text": text,
                "source": path.name,
            }
        )
    return documents


def build_collection():
    documents = load_documents()

    if len(documents) != 8:
        raise RuntimeError(f"Expected 8 documents, found {len(documents)}")

    model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    texts = [doc["text"] for doc in documents]
    ids = [doc["id"] for doc in documents]
    metadatas = [{"source": doc["source"]} for doc in documents]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
    ).tolist()

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print(f"Embedded and stored {len(documents)} documents.")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"ChromaDB path: {CHROMA_DIR}")


if __name__ == "__main__":
    build_collection()
