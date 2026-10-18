from functools import lru_cache
from typing import Protocol

from sentence_transformers import SentenceTransformer

from filingsiq.config import settings


class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


@lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    return SentenceTransformer(settings.embedding_model)


def embed(texts: list[str]) -> list[list[float]]:
    """Embed text using the provider selected in EMBEDDING_PROVIDER."""
    provider = settings.embedding_provider.lower()
    if provider == "local":
        return _model().encode(texts, normalize_embeddings=True, batch_size=32).tolist()
    if provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install the 'openai' package to use the OpenAI provider") from exc
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.embeddings.create(
            model=settings.openai_embedding_model,
            input=texts,
            dimensions=settings.embedding_dimensions,
        )
        return [item.embedding for item in response.data]
    raise ValueError("EMBEDDING_PROVIDER must be one of: local, openai")
