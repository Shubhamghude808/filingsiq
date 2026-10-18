from filingsiq.evals.run_evals import K, first_hit_rank, load_questions, is_hit
from filingsiq.retrieval.hybrid import search
for q in load_questions():
    if q.get("set") not in ("nvda", "paraphrase"):
        continue
    strict_rank = first_hit_rank(q, "hybrid", True, True)
    if strict_rank == 1:
        continue
    loose_rank = first_hit_rank(q, "hybrid", True, False)
    phrases = [p.lower() for p in q.get("must_contain", [])]
    print(f"\n{q['id']} [{q['set']}] section-level rank={loose_rank} strict rank={strict_rank}")
    print("  Q:", q["question"])
    print("  expect:", q["expected_section"], "| phrases:", q.get("must_contain"))
    for i, r in enumerate(search(q["question"], q.get("ticker"), K, q.get("fiscal_year"))[:5], 1):
        s = "S" if is_hit(q, r, False) else "-"
        p = "P" if any(ph in r["text"].lower() for ph in phrases) else "-"
        print(f"   {i}. {s}{p} {r['ticker']} FY{r['fiscal_year']} {r['section']:8} {r['text'][:60]!r}")
