export class FormatError extends Error {
  constructor(message) {
    super(message);
    this.name = 'FormatError';
  }
}

export function formatMessage(message, values = {}) {
  return message.replace(/\{([a-zA-Z_][a-zA-Z0-9_]*)\}/g, (match, name) => {
    if (!(name in values)) {
      throw new FormatError(`Missing value: ${name}`);
    }
    return String(values[name]);
  });
}
