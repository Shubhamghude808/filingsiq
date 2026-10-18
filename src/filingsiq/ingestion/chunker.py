def chunk_text(text: str, max_words: int = 220, overlap: int = 40) -> list[str]:
    """Word-window chunking with overlap. Swap for token-aware chunking later."""
    words = text.split()
    if not words:
        return []
    step = max_words - overlap
    return [" ".join(words[i : i + max_words]) for i in range(0, len(words), step)]
