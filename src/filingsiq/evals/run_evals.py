"""Retrieval eval: recall@k and MRR against the golden set, with ablations.
A hit = a chunk from an expected section, from the expected company, and from the
expected fiscal year if the question names one. With --strict, the chunk must also
contain at least one `must_contain` phrase (when the question defines any).
Usage:
  python -m filingsiq.evals.run_evals                  # comparison table
  python -m filingsiq.evals.run_evals --strict         # require the answer text
  python -m filingsiq.evals.run_evals --verbose        # per-question ranks
  python -m filingsiq.evals.run_evals --check-golden   # validate must_contain phrases
"""
import argparse
import json
from pathlib import Path
from filingsiq.db import get_conn
from filingsiq.retrieval.hybrid import search
GOLDEN = Path(__file__).parent / "golden" / "questions.jsonl"
K = 10  # keep fixed so runs are comparable
SETS = ["original", "paraphrase", "msft", "nvda", "cross"]
def load_questions() -> list[dict]:
    return [json.loads(line) for line in GOLDEN.read_text().splitlines() if line.strip()]
def _sections(q: dict) -> list[str]:
    s = q["expected_section"]
    return [s] if isinstance(s, str) else s
def _tickers(q: dict) -> list[str]:
    t = q.get("expected_ticker") or q.get("ticker")
    return [t] if isinstance(t, str) else list(t or [])
def is_hit(q: dict, r: dict, strict: bool = False) -> bool:
    tickers = _tickers(q)
    if tickers and r["ticker"] not in tickers:
        return False
    year_ok = q.get("fiscal_year") is None or r["fiscal_year"] == q["fiscal_year"]
    if not (year_ok and r["section"] in _sections(q)):
        return False
    if strict and q.get("must_contain"):
        text = r["text"].lower()
        return any(p.lower() in text for p in q["must_contain"])
    return True
def first_hit_rank(q: dict, mode: str, use_year: bool, strict: bool) -> int | None:
    fy = q.get("fiscal_year") if use_year else None
    for rank, r in enumerate(search(q["question"], q.get("ticker"), K, fy, mode), 1):
        if is_hit(q, r, strict):
            return rank
    return None
def summarize(ranks: list[int | None]) -> dict:
    n = max(len(ranks), 1)
    def recall(at: int) -> float:
        return sum(1 for r in ranks if r is not None and r <= at) / n
    return {
        "n": len(ranks),
        "r@1": recall(1),
        "r@3": recall(3),
        "r@5": recall(5),
        "mrr": sum(1 / r for r in ranks if r) / n,
    }
def check_golden(qs: list[dict]) -> None:
    """For each question with must_contain: does ANY chunk in the expected
    ticker/year/sections contain any phrase? If not, the phrase or section is wrong."""
    bad = 0
    with get_conn() as conn:
        for q in qs:
            phrases = q.get("must_contain")
            if not phrases:
                continue
            n = conn.execute(
                """SELECT count(*) FROM chunks c JOIN filings f USING (accession_no)
                   WHERE f.ticker = ANY(%s) AND (%s::int IS NULL OR f.fiscal_year = %s)
                     AND c.section = ANY(%s) AND c.text ILIKE ANY(%s)""",
                (_tickers(q), q.get("fiscal_year"), q.get("fiscal_year"),
                 _sections(q), [f"%{p}%" for p in phrases]),
            ).fetchone()[0]
            if n == 0:
                bad += 1
                print(f"NO MATCH  {q['id']}  {_tickers(q)}  {q['expected_section']}  {phrases}")
    print(f"\n{bad} question(s) have no chunk containing their must_contain phrases.")
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--check-golden", action="store_true")
    args = ap.parse_args()
    qs = load_questions()
    if args.check_golden:
        check_golden(qs)
    elif args.verbose:
        ranks = []
        for q in qs:
            rank = first_hit_rank(q, "hybrid", True, args.strict)
            ranks.append(rank)
            print(f"{q['id']} {q.get('set', 'original'):10} rank={rank}  "
                  f"{q['expected_section']}  {q['question'][:50]}")
        print(json.dumps(summarize(ranks), indent=2))
    else:
        print(f"{'mode':8} {'year':6} {'set':11} {'n':>3} {'r@1':>5} {'r@3':>5} {'r@5':>5} {'mrr':>6}")
        for mode in ("vector", "keyword", "hybrid"):
            for use_year in (False, True):
                ranks = [first_hit_rank(q, mode, use_year, args.strict) for q in qs]
                for s in SETS:
                    sub = [r for r, q in zip(ranks, qs) if q.get("set", "original") == s]
                    if not sub:
                        continue
                    m = summarize(sub)
                    print(f"{mode:8} {str(use_year):6} {s:11} {m['n']:3d} "
                          f"{m['r@1']:5.2f} {m['r@3']:5.2f} {m['r@5']:5.2f} {m['mrr']:6.3f}")
        print(f"\nk={K}, strict={args.strict}")
