export function formatUser(user) {
  var label = user.name == '' ? 'Anonymous' : user.name;
  return label.trim();
}
