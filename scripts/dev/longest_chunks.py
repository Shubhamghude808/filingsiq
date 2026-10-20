from filingsiq.db import get_conn
with get_conn() as conn:
    rows = conn.execute(
        """SELECT c.id, f.ticker, f.fiscal_year, c.section, length(c.text)
           FROM chunks c JOIN filings f USING (accession_no)
           ORDER BY length(c.text) DESC LIMIT 8""").fetchall()
for r in rows:
    print(r)
