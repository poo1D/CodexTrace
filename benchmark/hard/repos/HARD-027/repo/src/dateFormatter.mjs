import { format } from 'date-fns';

export class DateFormatError extends Error {}

export function formatDate(input, pattern = 'YYYY-MM-DD', options = {}) {
  const date = input instanceof Date ? input : new Date(input);
  if (Number.isNaN(date.getTime())) {
    throw new DateFormatError(`invalid date: ${input}`);
  }
  return format(date, pattern, options);
}
