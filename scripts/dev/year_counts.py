from collections import Counter
from filingsiq.evals.run_evals import load_questions
c = Counter()
for q in load_questions():
    s = q.get("set", "original")
    c[(s, "total")] += 1
    if q.get("fiscal_year") is None:
        c[(s, "no_year")] += 1
for s in ["original", "paraphrase", "msft", "nvda", "cross"]:
    print(f"{s:11} total={c[(s, 'total')]:3d}  no fiscal_year={c[(s, 'no_year')]:3d}")
