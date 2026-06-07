import time


class TTLCache:
    def __init__(self, now=None):
        self._now = now or time.monotonic
        self._values = {}

    def get_or_set(self, key, loader, ttl, stale_if_error=False):
        entry = self._values.get(key)
        now = self._now()
        if entry is not None and entry["expires_at"] > now:
            return entry["value"]

        value = loader()
        self._values[key] = {"value": value, "expires_at": self._now() + ttl}
        return value

    def clear(self):
        self._values.clear()
