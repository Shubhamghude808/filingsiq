import torch
from sentence_transformers import CrossEncoder
from filingsiq.db import get_conn
from filingsiq.retrieval.hybrid import search
NAME = "BAAI/bge-reranker-base"
q = "How many people does Apple employ?"
pool = search(q, "AAPL", 50, 2025, "hybrid")
with get_conn() as conn:
    row = conn.execute(
        """SELECT c.id, c.text, c.section FROM chunks c JOIN filings f USING (accession_no)
           WHERE f.ticker = 'AAPL' AND f.fiscal_year = 2025
             AND c.text ILIKE '%full-time equivalent employees%' LIMIT 1"""
    ).fetchone()
print("answer chunk found:", row is not None)
print("answer chunk in pool:", bool(row) and row[0] in [r["id"] for r in pool])
texts = [r["text"] for r in pool]
if row and row[0] not in [r["id"] for r in pool]:
    texts.append(row[1])
target_idx = None
if row:
    target_idx = next(i for i, t in enumerate(texts) if t == row[1])
good = (q, "The Company had approximately 150,000 full-time equivalent employees.")
bad = (q, "The weather in the city is sunny and mild today.")
for dev in ["cpu", "cuda"]:
    m = CrossEncoder(NAME, max_length=512, device=dev)
    s = [float(x) for x in m.predict([(q, t) for t in texts], batch_size=16)]
    g, b = [float(x) for x in m.predict([good, bad])]
    order = sorted(range(len(s)), key=lambda i: -s[i])
    print(f"\n[{dev}] sanity: good={g:.3f} bad={b:.3f}")
    if target_idx is not None:
        print(f"[{dev}] answer chunk score={s[target_idx]:.3f} rank={order.index(target_idx) + 1} of {len(s)}")
    for i in order[:3]:
        print(f"[{dev}]   {s[i]:.3f}  {texts[i][:70]!r}")
    del m
    torch.cuda.empty_cache()
