export function buildFilter(input) {
  if (input.op === 'eq') {
    return `${input.field} = ${quote(input.value)}`;
  }
  if (input.op === 'range') {
    return `${input.field} BETWEEN ${quote(input.min)} AND ${quote(input.max)}`;
  }
  if (input.op === 'contains') {
    return `${input.field} CONTAINS ${quote(input.value)}`;
  }
  throw new Error(`unknown filter op: ${input.op}`);
}

function quote(value) {
  if (typeof value === 'number') return String(value);
  return `'${String(value).replaceAll("'", "''")}'`;
}
