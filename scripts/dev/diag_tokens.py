from sentence_transformers import CrossEncoder
from filingsiq.db import get_conn
from filingsiq.retrieval.hybrid import search
tok = CrossEncoder("BAAI/bge-reranker-base", max_length=512, device="cpu").tokenizer
q = "How many people does Apple employ?"
phrase = "full-time equivalent employees"
def ntok(t):
    return len(tok(t, add_special_tokens=False)["input_ids"])
with get_conn() as conn:
    rows = conn.execute(
        """SELECT c.id, c.section, c.text FROM chunks c JOIN filings f USING (accession_no)
           WHERE f.ticker = 'AAPL' AND f.fiscal_year = 2025
             AND c.text ILIKE %s""", (f"%{phrase}%",)).fetchall()
print(f"chunks containing the phrase: {len(rows)}")
for cid, sec, text in rows:
    pos = text.lower().find(phrase)
    print(f"  id={cid} {sec}: {ntok(text)} tokens, phrase at token ~{ntok(text[:pos])}")
print("\ntop 3 hybrid chunks (token counts):")
for r in search(q, "AAPL", 3, 2025, "hybrid"):
    print(f"  {r['section']}: {ntok(r['text'])} tokens  {r['text'][:60]!r}")
allc = [r["text"] for r in search(q, "AAPL", 50, 2025, "hybrid")]
over = sum(1 for t in allc if ntok(t) > 500)
print(f"\nof the 50-chunk pool, {over} are over 500 tokens")
