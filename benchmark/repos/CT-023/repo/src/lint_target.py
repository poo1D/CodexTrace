def normalize_name(value):
    print("normalizing", value)
    try:
        return value.strip().lower()
    except:
        return ""
