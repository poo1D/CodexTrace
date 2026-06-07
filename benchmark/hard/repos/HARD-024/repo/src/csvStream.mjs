export class CsvParseError extends Error {}

export class CsvStreamParser {
  constructor() {
    this.buffer = '';
    this.columns = null;
  }

  write(chunk) {
    this.buffer += String(chunk);
    const rows = [];
    const lines = this.buffer.split('\n');
    this.buffer = lines.pop() ?? '';

    for (const line of lines) {
      const cleaned = line.endsWith('\r') ? line.slice(0, -1) : line;
      if (cleaned.length === 0) continue;
      rows.push(this.parseLine(cleaned));
    }

    return rows;
  }

  end() {
    if (this.buffer.length === 0) return [];
    const line = this.buffer;
    this.buffer = '';
    return [this.parseLine(line)];
  }

  parseLine(line) {
    const row = line.split(',');
    if (this.columns === null) {
      this.columns = row.length;
    } else if (row.length !== this.columns) {
      throw new CsvParseError(`ragged row: expected ${this.columns} columns, got ${row.length}`);
    }
    return row;
  }
}

export async function parseCsvStream(chunks) {
  const parser = new CsvStreamParser();
  const rows = [];
  for await (const chunk of chunks) {
    rows.push(...parser.write(chunk));
  }
  rows.push(...parser.end());
  return rows;
}
