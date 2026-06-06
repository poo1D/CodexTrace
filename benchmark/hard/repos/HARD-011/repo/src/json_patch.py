import copy


class PatchError(Exception):
    pass


def apply_patch(document, operations):
    result = copy.deepcopy(document)
    for operation in operations:
        op = operation["op"]
        path = operation["path"].strip("/").split("/") if operation["path"] else []
        target = result
        for part in path[:-1]:
            target = target[int(part)] if isinstance(target, list) else target[part]
        key = path[-1] if path else None
        if op in {"add", "replace"}:
            if key is None:
                result = operation["value"]
            elif isinstance(target, list):
                target[int(key)] = operation["value"]
            else:
                target[key] = operation["value"]
        elif op == "remove":
            if isinstance(target, list):
                target.pop(int(key))
            else:
                del target[key]
    return result
