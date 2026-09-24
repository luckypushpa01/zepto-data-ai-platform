# Zepto Support Assistant

## Overview

This module implements a small GenAI-style support assistant for Zepto policies. The default graded path is fully deterministic and offline using `MOCK_LLM=1`.

The system ingests eight Zepto policy documents, creates local embeddings with `all-MiniLM-L6-v2`, stores them in a local ChromaDB collection, retrieves the most relevant policy context, and produces a validated response through a LangGraph workflow.

## Architecture

```text
Zepto policy documents
        |
        v
support_assistant/docs/*.txt
        |
        v
ingest.py
        |
        +--> all-MiniLM-L6-v2 embeddings
        |
        v
ChromaDB: zepto_policies
        |
        v
FastAPI /ask
        |
        v
LangGraph
        |
        +--> classify_intent
        |       |
        |       +--> policy_question
        |       |        |
        |       |        v
        |       |   retrieve_and_answer
        |       |
        |       +--> general_question
        |                |
        |                v
        |          direct_answer
        |
        v
Pydantic AskResponse

## FastAPI `/ask` Examples

### 1. Policy retrieval question

Request:

```bash
curl -X POST http://127.0.0.1:7860/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"How long does Zepto delivery take?"}'                     
curl -X POST http://127.0.0.1:7860/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the capital of France?"}'




Example response:

```json
{
  "answer": "Zepto typically delivers orders within 10 to 30 minutes of order confirmation.",
  "sources": ["doc_01"],
  "confidence": 1.0
}### 2. General non-retrieval question

Example response:

```json
{
  "answer": "I can help with Zepto support and policy questions.",
  "sources": [],
  "confidence": 1.0
}