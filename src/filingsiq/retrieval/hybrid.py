"""Hybrid retrieval: vector + full-text, fused with Reciprocal Rank Fusion."""
import re

from filingsiq.config import settings
from filingsiq.db import get_conn
from filingsiq.ingestion.embedder import embed

MODES = ("hybrid", "vector", "keyword")
def _rrf(rankings: list[list[int]], k: int = 60) -> dict[int, float]:
    scores: dict[int, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return scores
def _or_query(text: str) -> str:
    """Build a safe PostgreSQL OR query while removing possessive artefacts."""
    raw = re.findall(r"[A-Za-z0-9]+(?:['’]s)?", text.lower())
    terms = [re.sub(r"['’]s$", "", token) for token in raw]
    return " | ".join(dict.fromkeys(token for token in terms if token != "s"))
def search(
    query: str,
    ticker: str | None = None,
    k: int = 20,
    fiscal_year: int | None = None,
    mode: str = "hybrid",
    rerank: bool = False,
    rerank_pool: int = 50,
) -> list[dict]:
    if settings.retrieval_backend.lower() != "postgres":
        raise ValueError(
            "RETRIEVAL_BACKEND is not supported yet: "
            f"{settings.retrieval_backend!r}. Available backend: postgres"
        )
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    where = ""
    if ticker:
        where += " AND f.ticker = %(ticker)s"
    if fiscal_year:
        where += " AND f.fiscal_year = %(fy)s"
    # When reranking, fuse a wider pool, rescore it, then cut to k.
    out_n = max(k, rerank_pool) if rerank else k
    params = {"tsq": _or_query(query), "k": max(out_n * 2, 50), "ticker": ticker, "fy": fiscal_year}
    vec_ids: list[int] = []
    txt_ids: list[int] = []
    with get_conn() as conn:
        if mode in ("hybrid", "vector"):
            params["v"] = embed([query])[0]
            vec_ids = [r[0] for r in conn.execute(
                f"""SELECT c.id FROM chunks c JOIN filings f USING (accession_no)
                    WHERE true {where}
                    ORDER BY c.embedding <=> %(v)s::vector LIMIT %(k)s""", params)]
        if mode in ("hybrid", "keyword"):
            txt_ids = [r[0] for r in conn.execute(
                f"""SELECT c.id FROM chunks c JOIN filings f USING (accession_no)
                    WHERE c.tsv @@ to_tsquery('english', %(tsq)s) {where}
                    ORDER BY ts_rank(c.tsv, to_tsquery('english', %(tsq)s)) DESC
                    LIMIT %(k)s""", params)]
        fused = sorted(
            _rrf([r for r in (vec_ids, txt_ids) if r]).items(), key=lambda x: -x[1]
        )[:out_n]
        if not fused:
            return []
        ids = [i for i, _ in fused]
        rows = conn.execute(
            """SELECT c.id, c.text, c.section, f.ticker, f.fiscal_year, f.accession_no
               FROM chunks c JOIN filings f USING (accession_no) WHERE c.id = ANY(%s)""",
            (ids,),
        ).fetchall()
    by_id = {r[0]: r for r in rows}
    results = [
        {"id": i, "score": s, "rrf_score": s, "text": by_id[i][1], "section": by_id[i][2],
         "ticker": by_id[i][3], "fiscal_year": by_id[i][4], "accession_no": by_id[i][5]}
        for i, s in fused if i in by_id
    ]
    if rerank:
        from filingsiq.retrieval.reranker import rerank_scores
        new_scores = rerank_scores(query, [r["text"] for r in results])
        for r, s in zip(results, new_scores):
            r["score"] = s
        results.sort(key=lambda r: -r["score"])
    return results[:k]
