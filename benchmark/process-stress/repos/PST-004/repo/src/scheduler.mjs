export async function runSequential(tasks) {
  return Promise.all(tasks.map((task) => task()));
}
