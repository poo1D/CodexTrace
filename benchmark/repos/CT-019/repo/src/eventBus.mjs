export class EventBus {
  constructor() {
    this.listeners = new Map();
  }

  on(name, listener) {
    if (!this.listeners.has(name)) this.listeners.set(name, []);
    this.listeners.get(name).push(listener);
    return () => {
      const next = this.listeners.get(name).filter((item) => item !== listener);
      this.listeners.set(name, next);
    };
  }

  once(name, listener) {
    const wrapped = (...args) => {
      const next = this.listeners.get(name).filter((item) => item !== wrapped);
      this.listeners.set(name, next);
      listener(...args);
    };
    if (!this.listeners.has(name)) this.listeners.set(name, []);
    this.listeners.get(name).push(wrapped);
  }

  emit(name, value) {
    for (const listener of this.listeners.get(name) || []) listener(value);
  }
}
