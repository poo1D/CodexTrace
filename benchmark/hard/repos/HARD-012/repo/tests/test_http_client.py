import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from http_client import Response, request_with_retry


class HttpClientTest(unittest.TestCase):
    def test_retries_429_with_retry_after_delta(self):
        calls = []
        slept = []

        def client(url):
            calls.append(url)
            if len(calls) == 1:
                return Response(429, headers={"Retry-After": "2"})
            return Response(200, "ok")

        response = request_with_retry(
            "https://example.invalid/data",
            client=client,
            max_attempts=3,
            sleep=slept.append,
        )

        self.assertEqual(response.status, 200)
        self.assertEqual(response.body, "ok")
        self.assertEqual(calls, ["https://example.invalid/data", "https://example.invalid/data"])
        self.assertEqual(slept, [2])


if __name__ == "__main__":
    unittest.main()
