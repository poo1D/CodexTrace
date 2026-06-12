import json


def export_json(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle)
