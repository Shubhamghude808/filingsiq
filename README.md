# FilingsIQ

SEC filings research agent: hybrid retrieval, structured financials, multi-agent
reasoning, and measurable accuracy.

## Quickstart
```bash
cp .env.example .env        # set SEC_USER_AGENT
make up                     # Postgres+pgvector, Redis
make install
make ingest                 # AAPL, MSFT, NVDA, last 3 10-Ks
make api                    # http://localhost:8000/docs
make eval                   # recall@k, MRR on the golden set
```

## Provider configuration

The application uses stable internal `embed()` and `search()` interfaces, so
providers can be changed through `.env` without changing ingestion, API, or
agent code. The defaults keep the current local setup:

```dotenv
EMBEDDING_PROVIDER=local
RETRIEVAL_BACKEND=postgres
```

To use OpenAI embeddings instead, set `OPENAI_API_KEY` and change only:

```dotenv
EMBEDDING_PROVIDER=openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=384
```

When changing embedding models, re-ingest existing filings because stored
vectors must have the same dimensions and embedding space as query vectors.

## Roadmap
- [x] Scaffold, ingestion, hybrid search, eval harness
- [ ] Golden set (100+ verified questions)
- [ ] XBRL financials + SQL tool
- [ ] Planner / specialist / critic agents (LangGraph)
- [ ] Filing diff pipeline
- [ ] Fine-tuned reranker
- [ ] Async ingestion, K8s, load tests

## Results
| Stage | recall@5 | MRR | Notes |
|---|---|---|---|
| Baseline | - | - | |
