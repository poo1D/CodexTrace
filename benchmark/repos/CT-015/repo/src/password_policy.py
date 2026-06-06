def validation_errors(password):
    errors = []
    if len(password) < 12:
        errors.append("minimum length")
    if not any(char.isdigit() for char in password):
        errors.append("digit required")
    if not any(not char.isalnum() for char in password):
        errors.append("symbol required")
    return errors
