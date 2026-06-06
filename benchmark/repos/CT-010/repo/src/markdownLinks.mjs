export function extractLinks(markdown) {
  const matches = [...markdown.matchAll(/\[([^\]]+)\]\(([^)]+)\)/g)];
  return matches.map((match) => ({ text: match[1], href: match[2] }));
}
