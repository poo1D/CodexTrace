export class RangeSetError extends Error {
  constructor(message) {
    super(message);
    this.name = 'RangeSetError';
  }
}

export class RangeSet {
  constructor(ranges = []) {
    this.ranges = ranges;
  }

  add(start, end) {
    this.ranges.push([start, end]);
    return this;
  }

  remove(start, end) {
    this.ranges = this.ranges.filter(([rangeStart, rangeEnd]) => {
      return rangeEnd < start || rangeStart > end;
    });
    return this;
  }

  contains(value) {
    return this.ranges.some(([start, end]) => start <= value && value <= end);
  }

  union(other) {
    this.ranges.push(...other.toArray());
    return this;
  }

  toArray() {
    return this.ranges.slice();
  }
}
