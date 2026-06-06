def matches_path(pattern, path):
    pattern_parts = pattern.split("/")
    path_parts = path.split("/")
    if len(pattern_parts) != len(path_parts):
        return False
    for pattern_part, path_part in zip(pattern_parts, path_parts):
        if pattern_part == "*":
            continue
        if pattern_part != path_part:
            return False
    return True
