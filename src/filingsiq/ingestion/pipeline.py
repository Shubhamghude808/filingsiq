from filingsiq.db import get_conn
from filingsiq.ingestion.chunker import chunk_text
from filingsiq.ingestion.edgar_client import RawFiling, fetch_10ks
from filingsiq.ingestion.embedder import embed
from filingsiq.ingestion.parser import html_to_text, split_sections


def already_ingested(accession_no: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM chunks WHERE accession_no = %s LIMIT 1", (accession_no,)
        ).fetchone()
    return row is not None


def ingest_filing(f: RawFiling, force: bool = False) -> int:
    if not force and already_ingested(f.accession_no):
        return 0
    sections = split_sections(html_to_text(f.html))
    rows: list[tuple[str, int, str]] = []
    for label, body in sections:
        for i, chunk in enumerate(chunk_text(body)):
            if len(chunk.split()) < 40:
                continue
            rows.append((label, i, chunk))
    if not rows:
        return 0

    vectors = embed([r[2] for r in rows])
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO filings (accession_no, ticker, form_type, fiscal_year, filed_at, url)
               VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""",
            (f.accession_no, f.ticker, f.form_type, f.fiscal_year, f.filed_at, f.url),
        )
        conn.execute("DELETE FROM chunks WHERE accession_no = %s", (f.accession_no,))
        with conn.cursor() as cur:
            cur.executemany(
                """INSERT INTO chunks (accession_no, section, chunk_index, text, embedding)
                   VALUES (%s,%s,%s,%s,%s)""",
                [(f.accession_no, s, i, t, v) for (s, i, t), v in zip(rows, vectors)],
            )
        conn.commit()
    return len(rows)


def ingest_ticker(ticker: str, years: int = 3, force: bool = False) -> int:
    return sum(ingest_filing(f, force) for f in fetch_10ks(ticker, years))
