import sys
from filingsiq.ingestion.edgar_client import fetch_10ks
from filingsiq.ingestion.parser import html_to_text, ITEM_RE
ticker = sys.argv[1] if len(sys.argv) > 1 else "MSFT"
f = fetch_10ks(ticker, 1)[0]
lines = html_to_text(f.html).splitlines()
print(ticker, "total lines:", len(lines))
print("\n--- lines the parser treats as Item headings ---")
for n, line in enumerate(lines):
    if ITEM_RE.match(line) and len(line) < 150:
        print(n, repr(line[:70]))
print("\n--- lines containing 'risk factors' (short ones) ---")
for n, line in enumerate(lines):
    if "risk factors" in line.lower() and len(line) < 80:
        print(n, repr(line[:70]))
