class TTLCache:
    def __init__(self, now):
        self.now = now
        self._items = {}

    def set(self, key, value, ttl):
        self._items[key] = (value, self.now() + ttl)

    def get(self, key):
        if key not in self._items:
            return None
        value, expires_at = self._items[key]
        if self.now() >= expires_at:
            del self._items[key]
            return None
        return value
