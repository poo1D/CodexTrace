def parse_records(text):
    rows = []
    for line in text.splitlines():
        if not line.strip():
            continue
        rows.append(line.split(","))
    return rows
