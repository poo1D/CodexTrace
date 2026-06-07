export class BatchQueue {
  constructor(handler) {
    this.handler = handler;
    this.items = [];
  }

  push(item) {
    this.items.push(item);
  }

  size() {
    return this.items.length;
  }

  flush() {
    const pending = this.items;
    this.items = [];
    const results = [];
    for (const item of pending) {
      results.push(this.handler(item));
    }
    return results;
  }
}
