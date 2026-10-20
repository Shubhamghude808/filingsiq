import time
from filingsiq.retrieval.hybrid import search
search("warm up", "AAPL", 10, None, "hybrid", rerank=True)
t = time.perf_counter()
for _ in range(5):
    search("Is anyone suing Apple?", "AAPL", 10, 2025, "hybrid", rerank=True)
print(f"{(time.perf_counter() - t) / 5:.2f} s/query (warm)")
