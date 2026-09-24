from fastapi import FastAPI

from .graph import answer_query
from .models import AskRequest, AskResponse


app = FastAPI(
    title="Zepto Support Assistant",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "Zepto Support Assistant is running."}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    return answer_query(request.query)
