from filingsiq.evals.run_evals import load_questions, is_hit, K
from filingsiq.retrieval.hybrid import search
def rank_of(q, res):
    for i, r in enumerate(res, 1):
        if is_hit(q, r, False):
            return i
    return None
qs = load_questions()
search("warm up", "AAPL", K, None, "hybrid", rerank=True)
worse = better = 0
for q in qs:
    fy = q.get("fiscal_year")
    base = search(q["question"], q.get("ticker"), K, fy, "hybrid")
    rr = search(q["question"], q.get("ticker"), K, fy, "hybrid", rerank=True)
    b, a = rank_of(q, base), rank_of(q, rr)
    if b == a:
        continue
    if a is None or (b is not None and a > b):
        tag = "WORSE"; worse += 1
    else:
        tag = "BETTER"; better += 1
    print(f"\n{tag} {q['id']} [{q.get('set', 'original')}] {b} -> {a}  expected={q['expected_section']}")
    print(f"  Q: {q['question'][:80]}")
    for r in rr[:3]:
        print(f"  {r['section']:<10} {r['text'][:90]!r}")
print(f"\nworse={worse} better={better}")
