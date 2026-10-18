from filingsiq.evals.run_evals import K, first_hit_rank, is_hit, load_questions
from filingsiq.retrieval.hybrid import search
for q in load_questions():
    rank = first_hit_rank(q, "hybrid", True, False)
    if rank == 1:
        continue
    print(f"\n{q['id']} [{q.get('set', 'original')}] rank={rank} expect={q['expected_section']}")
    print("  Q:", q["question"])
    results = search(q["question"], q.get("ticker"), K, q.get("fiscal_year"))
    for i, r in enumerate(results[:5], 1):
        mark = "HIT" if is_hit(q, r) else "   "
        print(f"   {i}. {mark} {r['ticker']} FY{r['fiscal_year']} {r['section']:8} {r['text'][:60]!r}")
