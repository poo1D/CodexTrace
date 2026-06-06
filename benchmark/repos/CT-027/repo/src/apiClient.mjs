export function errorForStatus(status) {
  if (status >= 500) return 'server_error';
  if (status === 401) return 'unauthorized';
  if (status === 404) return 'server_error';
  return 'unknown_error';
}
