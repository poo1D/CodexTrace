def parse_frontmatter(text):
    if not text.startswith("---\n"):
        return {}, text
    end = text.index("\n---\n", 4)
    header = text[4:end].strip()
    body = text[end + 5:]
    metadata = {}
    for line in header.splitlines():
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata, body
