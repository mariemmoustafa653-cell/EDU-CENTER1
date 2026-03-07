def chunk_text(text: str, max_tokens: int = 900, overlap: int = 50) -> list[str]:
    words = text.split()
    if len(words) <= max_tokens:
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + max_tokens, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap if end < len(words) else end

    return chunks
