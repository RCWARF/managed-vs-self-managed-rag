def chunk_text(text, size, overlap):
        chunks = []
        start = 0
        while start < len(text):
            end = start + size
            chunks.append(text[start:end])
            start += size - overlap
        return [c for c in chunks if c.strip()]