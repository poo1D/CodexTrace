export function matchRoute(routes, path) {
  return routes.find((route) => route.path === path) || null;
}
