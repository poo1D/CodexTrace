export function resolveSettings(defaults, userSettings) {
  return {
    theme: 'light',
    notifications: true,
    ...userSettings,
    ...defaults,
  };
}
