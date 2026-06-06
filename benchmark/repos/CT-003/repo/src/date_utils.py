from datetime import datetime


def parse_iso_datetime(value):
    return datetime.fromisoformat(value)
