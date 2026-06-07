export function validateRegistration(input) {
  const data = input ?? {};

  if (!data.email || !String(data.email).includes('@')) {
    return invalid('email', 'invalid_email', 'email must contain @');
  }

  if (!data.password || String(data.password).length < 8) {
    return invalid('password', 'weak_password', 'password must be at least 8 characters');
  }

  if (!Array.isArray(data.roles) || data.roles.length === 0) {
    return invalid('roles', 'missing_roles', 'at least one role is required');
  }

  return {
    valid: true,
    errors: [],
    value: {
      email: String(data.email).trim().toLowerCase(),
      password: data.password,
      roles: [...data.roles],
    },
  };
}

function invalid(field, code, message) {
  return {
    valid: false,
    errors: [{ field, code, message }],
    value: null,
  };
}
