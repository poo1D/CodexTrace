import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from event_writer import EventWriter, MemoryEventWriter, publish_events


class EventWriterTest(unittest.TestCase):
    def test_memory_writer_conforms_to_protocol(self):
        writer = MemoryEventWriter()
        self.assertIsInstance(writer, EventWriter)
        self.assertEqual(writer.write("hello\n"), len("hello\n"))
        writer.flush()
        self.assertEqual(writer.messages, ["hello\n"])
        self.assertTrue(writer.flushed)

    def test_publish_events_uses_memory_writer(self):
        writer = publish_events(["created", "closed"])
        self.assertEqual(writer.messages, ["event: created\n", "event: closed\n"])
        self.assertTrue(writer.flushed)


if __name__ == "__main__":
    unittest.main()
