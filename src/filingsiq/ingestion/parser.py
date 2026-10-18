import re

from bs4 import BeautifulSoup

ITEM_RE = re.compile(r"^\s*item\s+(\d+[abc]?)\.?\s*[-–—:.]?\s*(.*)$", re.IGNORECASE)
FOOTER_RE = re.compile(r"[A-Z][\w.,&' ]{0,40}\|\s*\d{4} Form 10-[KQ]\s*\|\s*\d+")
# A line is a section heading only if its title matches the standard 10-K title.
ITEM_TITLES = {
    "1": "business", "1A": "risk factors", "1B": "unresolved", "1C": "cybersecurity",
    "2": "properties", "3": "legal proceedings", "4": "mine safety", "5": "market for",
    "6": "reserved", "7": "management", "7A": "quantitative", "8": "financial statements",
    "9": "changes in", "9A": "controls", "9B": "other information", "9C": "disclosure regarding",
    "10": "directors", "11": "executive compensation", "12": "security ownership",
    "13": "certain relationships", "14": "principal account", "15": "exhibit",
    "16": "form 10-k",
}
BLOCK_TAGS = ["p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6", "table", "section"]
def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    # Keep table rows on one line so numbers stay next to their labels.
    for tr in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        tr.replace_with(" | ".join(c for c in cells if c) + "\n")
    # Only block-level tags start a new line, so inline spans stay joined.
    for tag in soup.find_all(BLOCK_TAGS):
        tag.insert_before("\n")
        tag.insert_after("\n")
    text = FOOTER_RE.sub("", soup.get_text(""))
    return re.sub(r"\n{3,}", "\n\n", text)
def heading_label(line: str) -> str | None:
    if len(line) >= 150:
        return None
    m = ITEM_RE.match(line)
    if not m:
        return None
    num = m.group(1).upper()
    title = m.group(2).lower().lstrip("[ ")
    expected = ITEM_TITLES.get(num)
    if num == "7" and title.startswith("md&a"):
        return "Item 7"
    if expected and title.startswith(expected):
        return f"Item {num}"
    return None
def split_sections(text: str) -> list[tuple[str, str]]:
    """Split filing text into (section_label, body) using real 'Item X' headings."""
    raw: list[tuple[str, list[str]]] = [("preamble", [])]
    for line in text.splitlines():
        label = heading_label(line)
        if label:
            raw.append((label, []))
        else:
            raw[-1][1].append(line)
    bodies = [(label, "\n".join(body).strip()) for label, body in raw]
    # If a label still appears more than once (e.g. a table of contents without
    # pipes), keep the occurrence with the longest body; fold the rest into preamble.
    best: dict[str, int] = {}
    for i, (label, body) in enumerate(bodies):
        if label != "preamble" and (label not in best or len(body) > len(bodies[best[label]][1])):
            best[label] = i
    preamble: list[str] = []
    sections: list[tuple[str, str]] = []
    for i, (label, body) in enumerate(bodies):
        if label == "preamble" or best[label] != i:
            preamble.append(body)
        else:
            sections.append((label, body))
    pre = "\n".join(p for p in preamble if p).strip()
    result = [("preamble", pre)] if pre else []
    return result + [(label, body) for label, body in sections if body]
