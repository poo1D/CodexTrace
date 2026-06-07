import time


class SlidingLimiter:
    def __init__(self, limit, window_seconds, clock=None):
        self.limit = limit
        self.window_seconds = window_seconds
        self.clock = clock or time.time
        self._bucket = None
        self._count = 0

    def allow(self, user_id, now=None):
        if now is None:
            now = self.clock()
        bucket = int(now // self.window_seconds)
        if bucket != self._bucket:
            self._bucket = bucket
            self._count = 0
        if self._count >= self.limit:
            return False
        self._count += 1
        return True
