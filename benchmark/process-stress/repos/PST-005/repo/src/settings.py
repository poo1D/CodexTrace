def resolve_settings(defaults, file_settings=None, env=None, cli=None):
    result = dict(defaults)
    for source in (file_settings or {}, cli or {}, env or {}):
        result.update(source)
    return result
