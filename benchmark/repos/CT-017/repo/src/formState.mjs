export function validateForm(values) {
  const errors = {};
  if (values.name !== undefined) {
    if (values.name.trim() === '') {
      errors.name = 'Name is required';
    }
  } else {
    errors.name = 'Name is required';
  }
  if (values.email !== undefined) {
    if (!values.email.includes('@')) {
      errors.email = 'Email is invalid';
    }
  } else {
    errors.email = 'Email is invalid';
  }
  return errors;
}
