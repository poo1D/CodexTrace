export function debounce(fn, delayMs, options = {}) {
  let timer = null;
  return (...args) => {
    const shouldCallNow = options.leading && timer === null;
    clearTimeout(timer);
    timer = setTimeout(() => {
      timer = null;
      if (!options.leading) fn(...args);
    }, delayMs);
    if (shouldCallNow) fn(...args);
  };
}
