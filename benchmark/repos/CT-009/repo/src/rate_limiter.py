class SlidingWindowLimiter:
    def __init__(self, limit, window_seconds, allowlist=None):
        self.limit = limit
        self.window_seconds = window_seconds
        self.allowlist = set(allowlist or [])
        self.events = {}

    def allow(self, user_id, timestamp):
        events = [
            t for t in self.events.get(user_id, [])
            if timestamp - t < self.window_seconds
        ]
        allowed = len(events) < self.limit
        if allowed:
            events.append(timestamp)
        self.events[user_id] = events
        return allowed
