def evaluate_flag(config, flag_name, user):
    flags = config.get("flags", {})
    if flag_name not in flags:
        return bool(config.get("default", False))

    flag = flags[flag_name]
    if "enabled" in flag:
        return bool(flag["enabled"])

    return bool(config.get("default", False))
