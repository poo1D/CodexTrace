def search(items, query):
    """Return items that contain query."""
    return [item for item in items if query in item]
