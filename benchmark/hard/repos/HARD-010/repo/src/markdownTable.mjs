export function parseTable(markdown) {
  return markdown.trim().split('\n').map((line) =>
    line.replace(/^\||\|$/g, '').split('|').map((cell) => cell.trim())
  );
}
