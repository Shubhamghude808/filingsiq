import argparse

from filingsiq.ingestion.pipeline import ingest_ticker

p = argparse.ArgumentParser()
p.add_argument("--tickers", nargs="+", required=True)
p.add_argument("--years", type=int, default=3)
p.add_argument("--force", action="store_true", help="re-ingest even if already stored")
args = p.parse_args()

for t in args.tickers:
    n = ingest_ticker(t, args.years, args.force)
    print(f"{t}: {n} chunks ingested")