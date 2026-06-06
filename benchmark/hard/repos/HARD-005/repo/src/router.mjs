export function matchRoute(pattern, path) {
  if (pattern === path) return { matched: true, params: {} };
  return { matched: false, params: {} };
}
