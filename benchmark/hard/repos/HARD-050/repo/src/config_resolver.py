class ConfigError(Exception):
    pass


def resolve_config(defaults, env=None, cli=None, schema=None):
    env = env or {}
    cli = cli or {}
    config = defaults.copy()

    for name, value in env.items():
        if not name.startswith("APP_"):
            continue
        key = name[4:].lower()
        config[key] = value

    for key, value in cli.items():
        if value:
            config[key] = value

    return config
