def can_access(user, action, matrix):
    role = user.get("role")
    permissions = matrix.get(role, {})
    if action in user.get("allow", []):
        return True
    if action in user.get("deny", []):
        return False
    return action in permissions.get("allow", [])
