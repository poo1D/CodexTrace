def can_book(user, day_name):
    if day_name.lower() in {"saturday", "sunday"}:
        return False
    return True
