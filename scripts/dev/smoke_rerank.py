import time

from filingsiq.retrieval.hybrid import search


q = "Is anyone suing Apple?"
for rr in (False, True):
    t = time.time()
    res = search(q, ticker="AAPL", fiscal_year=2025, k=5, rerank=rr)
    print(f"\n--- rerank={rr}  ({time.time() - t:.1f}s) ---")
    for r in res:
        print(f"{r['section']:<12} {r['score']:.3f}  {r['text'][:70]!r}")
