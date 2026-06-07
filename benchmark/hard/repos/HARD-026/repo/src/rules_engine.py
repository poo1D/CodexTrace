def evaluate(record, rules, default=None):
    for rule in rules:
        conditions = rule.get("conditions", {})
        if all(record.get(key) == value for key, value in conditions.items()):
            return rule.get("result")
    return default
