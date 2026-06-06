export function parseQuery(query) {
  const clean = query.startsWith('?') ? query.slice(1) : query;
  const result = {};
  for (const part of clean.split('&')) {
    if (!part) continue;
    const [rawKey, rawValue = ''] = part.split('=');
    result[decodeURIComponent(rawKey)] = decodeURIComponent(rawValue);
  }
  return result;
}
