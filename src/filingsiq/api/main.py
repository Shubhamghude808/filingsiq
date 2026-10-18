from fastapi import FastAPI
from pydantic import BaseModel

from filingsiq.retrieval.hybrid import search

app = FastAPI(title="FilingsIQ")


class Query(BaseModel):
    question: str
    ticker: str | None = None
    fiscal_year: int | None = None
    k: int = 8


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/search")
def search_endpoint(q: Query):
    return {"results": search(q.question, q.ticker, q.k, q.fiscal_year)}
