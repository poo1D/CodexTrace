from dataclasses import dataclass, field


@dataclass
class Response:
    status: int
    body: str = ""
    headers: dict[str, str] = field(default_factory=dict)


def request_with_retry(url, client, max_attempts=3, sleep=None, now=None):
    return client(url)
