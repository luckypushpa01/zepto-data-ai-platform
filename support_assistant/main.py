from fastapi import FastAPI
from pydantic import BaseModel

from .rag import answer_query

app = FastAPI(title="Zepto Support Assistant")


class AskRequest(BaseModel):
    query: str


@app.post("/ask")
def ask(request: AskRequest):
    return answer_query(request.query)