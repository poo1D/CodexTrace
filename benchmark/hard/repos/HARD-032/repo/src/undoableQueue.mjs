export class UndoableQueue {
  constructor(items = []) {
    this.items = [...items];
    this.undoStack = [];
    this.redoStack = [];
  }

  get size() {
    return this.items.length;
  }

  enqueue(item) {
    this._save();
    this.items.push(item);
    this.redoStack = [];
    return this;
  }

  dequeue() {
    if (this.items.length === 0) {
      return undefined;
    }
    this._save();
    this.redoStack = [];
    return this.items.shift();
  }

  clear() {
    this._save();
    this.items = [];
    return this;
  }

  undo() {
    if (this.undoStack.length === 0) {
      return false;
    }
    this.redoStack.push([...this.items]);
    this.items = this.undoStack.pop();
    return true;
  }

  redo() {
    if (this.redoStack.length === 0) {
      return false;
    }
    this.undoStack.push([...this.items]);
    this.items = this.redoStack.pop();
    return true;
  }

  peek() {
    return this.items[0];
  }

  toArray() {
    return [...this.items];
  }

  _save() {
    this.undoStack.push([...this.items]);
  }
}
