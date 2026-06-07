import importlib
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "src"))


def run_visible_tests():
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        print(result.stdout)
        raise SystemExit(result.returncode)


run_visible_tests()
mod = importlib.import_module("event_writer")

assert getattr(mod.EventWriter, "_is_runtime_protocol", False), "EventWriter must be runtime-checkable"

class RecordingWriter:
    def __init__(self):
        self.messages = []
        self.flush_calls = 0

    def write(self, message: str) -> int:
        self.messages.append(message)
        return len(message)

    def flush(self) -> None:
        self.flush_calls += 1

recorder = RecordingWriter()
assert isinstance(recorder, mod.EventWriter), "foreign structural writer should satisfy EventWriter"

returned = mod.publish_events(["alpha", "beta"], recorder)
assert returned is recorder
assert recorder.messages == ["event: alpha\n", "event: beta\n"]
assert recorder.flush_calls == 1, "publish_events should flush once after writing all events"

memory = mod.MemoryEventWriter()
assert isinstance(memory, mod.EventWriter)
assert memory.write("direct\n") == len("direct\n")
assert memory.messages == ["direct\n"]
memory.flush()
assert memory.flushed is True

class PartialWriter:
    def write(self, message: str) -> int:
        return len(message)

assert not isinstance(PartialWriter(), mod.EventWriter), "flush must remain part of the protocol"

source = (ROOT / "src" / "event_writer.py").read_text(encoding="utf-8")
assert "Protocol" in source
assert "@runtime_checkable" in source
