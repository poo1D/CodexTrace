class WindowJoiner:
    def __init__(self, tolerance_ms):
        self.tolerance_ms = tolerance_ms
        self.left = []
        self.right = []
        self.watermark = None
        self.late_count = 0

    def add_left(self, event):
        if self.watermark is not None and event["time"] < self.watermark:
            self.late_count += 1
            return []
        emitted = []
        for right in self.right:
            if abs(event["time"] - right["time"]) <= self.tolerance_ms:
                emitted.append((event, right))
        self.left.append(event)
        return emitted

    def add_right(self, event):
        if self.watermark is not None and event["time"] < self.watermark:
            self.late_count += 1
            return []
        emitted = []
        for left in self.left:
            if abs(left["time"] - event["time"]) <= self.tolerance_ms:
                emitted.append((left, event))
        self.right.append(event)
        return emitted

    def advance_watermark(self, time_ms):
        self.watermark = time_ms
        self.left = [event for event in self.left if event["time"] >= time_ms]
        self.right = [event for event in self.right if event["time"] >= time_ms]
        return []

    def snapshot(self):
        return {
            "left": self.left,
            "right": self.right,
            "watermark": self.watermark,
            "late_count": self.late_count,
        }
