export async function loadAsset(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error('missing asset');
  return response.text();
}
