from dataclasses import dataclass


@dataclass
class Item:
    name: str
    count: int


def parse_item(data: dict[str, str]) -> Item:
    return Item(name=data["name"], count=data["count"])
