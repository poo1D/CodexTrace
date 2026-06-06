import json


def load_config(path, environ=None):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)
