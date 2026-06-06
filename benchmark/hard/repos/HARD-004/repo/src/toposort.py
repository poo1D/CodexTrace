class CycleError(Exception):
    pass


def topological_sort(graph):
    result = []
    seen = set()
    for node, deps in graph.items():
        if node in seen:
            continue
        seen.add(node)
        result.extend(dep for dep in deps if dep not in seen)
        seen.update(deps)
        result.append(node)
    return result
