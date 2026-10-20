"""Cross-encoder reranker. Loaded lazily so plain searches don't pay for it."""
import os

import torch
from sentence_transformers import CrossEncoder

DEFAULT_MODEL = "BAAI/bge-reranker-base"
_model: CrossEncoder | None = None
def _get_model() -> CrossEncoder:
    global _model
    if _model is None:
        name = os.environ.get("RERANKER_MODEL", DEFAULT_MODEL)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[reranker] {name} on {device}")
        _model = CrossEncoder(name, max_length=512, device=device)
    return _model
def rerank_scores(query: str, texts: list[str]) -> list[float]:
    """Score each (query, text) pair jointly. Higher means more relevant."""
    if not texts:
        return []
    scores = _get_model().predict([(query, t) for t in texts], batch_size=16)
    return [float(s) for s in scores]
