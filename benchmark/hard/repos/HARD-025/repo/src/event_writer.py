from typing import Protocol


class EventWriter(Protocol):
    def write(self, message: str) -> int:
        ...

    def flush(self) -> None:
        ...


class MemoryEventWriter:
    def __init__(self):
        self.messages = []
        self.flushed = False

    def append(self, message: str) -> None:
        self.messages.append(message)

    def drain(self) -> None:
        self.flushed = True


def publish_events(events, writer=None):
    if writer is None:
        writer = MemoryEventWriter()
    for event in events:
        writer.append(f"event: {event}\n")
    writer.drain()
    return writer
