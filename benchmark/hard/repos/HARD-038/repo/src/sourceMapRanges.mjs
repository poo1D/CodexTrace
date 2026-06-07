export class SourceMapError extends Error {
  constructor(message) {
    super(message);
    this.name = 'SourceMapError';
  }
}

export function mapRange(map, start, end) {
  const startOriginal = findExact(map.mappings, start);
  const endOriginal = findExact(map.mappings, end);
  if (!startOriginal || !endOriginal) {
    return null;
  }
  return {
    source: startOriginal.source,
    start: {
      line: startOriginal.line,
      column: startOriginal.column + 1,
    },
    end: {
      line: endOriginal.line,
      column: endOriginal.column + 1,
    },
  };
}

function findExact(mappings, position) {
  for (const entry of mappings || []) {
    if (
      entry.generated.line === position.line &&
      entry.generated.column === position.column
    ) {
      return entry.original;
    }
  }
  return null;
}
