def import_users(rows):
    users = []
    for row in rows:
        if not row.get("name"):
            raise ValueError("missing name")
        if "@" not in row.get("email", ""):
            raise ValueError("invalid email")
        users.append({"name": row["name"], "email": row["email"]})
    return users


def import_admins(rows):
    admins = []
    for row in rows:
        if not row.get("name"):
            raise ValueError("missing name")
        if "@" not in row.get("email", ""):
            raise ValueError("invalid email")
        admins.append({"name": row["name"], "email": row["email"], "role": "admin"})
    return admins
