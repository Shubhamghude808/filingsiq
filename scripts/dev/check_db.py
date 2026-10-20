from filingsiq.db import get_conn
with get_conn() as conn:
    print("chunks:", conn.execute("select count(*) from chunks").fetchone()[0])
    print("filings:", conn.execute("select count(*) from filings").fetchone()[0])
