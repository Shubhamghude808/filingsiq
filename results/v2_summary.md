## Reranker experiment (v2)
Hybrid retrieval + fiscal-year filter, k=10, 80 questions, 9-filing database.
| Config | pooled r@1 | pooled r@5 | pooled MRR | s/query |
|---|---|---|---|---|
| Hybrid (no reranker) | 0.83 | 0.96 | 0.88 | 0.13 |
| + bge-reranker-base | 0.65 | 0.85 | 0.73 | 2.85 |
| + MiniLM-L-6 | 0.79 | 0.96 | 0.86 | 0.48 |
Pooled values are computed from the per-set tables in results/ (rounded inputs, so
they may be off by about a question). Neither reranker improved retrieval, so it
stays off by default (`search(..., rerank=False)`).
Notes:
- Raw tables: results/v2_rerank.txt (bge) and results/v2_rerank_minilm.txt.
- results/v2_rerank_diff.txt lists per-question rank changes for bge. Odd characters
  such as "Æ" in it come from console encoding when the file was saved.
- The strict-mode rerank run was not completed and is not reported.
