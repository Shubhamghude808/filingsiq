from filingsiq.db import get_conn
with get_conn() as conn:
    print("filings and chunk counts:")
    for r in conn.execute("""SELECT f.ticker, f.fiscal_year, count(*)
        FROM chunks c JOIN filings f USING (accession_no)
        GROUP BY 1, 2 ORDER BY 1, 2"""):
        print(" ", r)
    print("\nper section: n, avg chars, max chars, chunks over 4000 chars")
    for r in conn.execute("""SELECT c.section, count(*), round(avg(length(c.text))),
        max(length(c.text)), count(*) FILTER (WHERE length(c.text) > 4000)
        FROM chunks c GROUP BY 1 ORDER BY 5 DESC, 2 DESC"""):
        print(" ", r)
