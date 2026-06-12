export function isEnabled(flags, name, user) {
  const flag = flags[name];
  return Boolean(flag && flag.enabled);
}
