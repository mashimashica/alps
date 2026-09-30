/*
 * The cron expressions of `schedules` in alps-harness.yaml: the five fields of crontab(5), minute,
 * hour, day of the month, month, and day of the week, read in the local time of the machine that
 * runs the harness server. A field is `*`, a value, or a range `a-b`; `*` and a range may take a
 * step after a slash (`9-17/2`; `*` with `/15` for every 15 minutes); a field may also be a list
 * of these separated by commas. Months and days of the week may be named by their first three
 * letters (`jan`, `mon-fri`); 0 and 7 are both Sunday.
 * As in cron, when the day of the month and the day of the week are both restricted (neither
 * starts with `*`), a day matches either of them; otherwise it must match both.
 */

export interface CronExpression {
  source: string;
  minutes: ReadonlySet<number>;
  hours: ReadonlySet<number>;
  days: ReadonlySet<number>;
  months: ReadonlySet<number>;
  weekdays: ReadonlySet<number>;
  /** Whether the day of the month or the day of the week starts with `*`. */
  starredDay: boolean;
}

/** A cron expression that cannot be read; the message says which field is wrong and why. */
export class CronError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "CronError";
  }
}

interface Field {
  name: string;
  min: number;
  max: number;
  /** A Map, so that no property every object inherits (`constructor`, `__proto__`) reads as a name. */
  names?: ReadonlyMap<string, number>;
}

const MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"];
const WEEKDAYS = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"];

const FIELDS: readonly Field[] = [
  { name: "minute", min: 0, max: 59 },
  { name: "hour", min: 0, max: 23 },
  { name: "day of the month", min: 1, max: 31 },
  {
    name: "month",
    min: 1,
    max: 12,
    names: new Map(MONTHS.map((name, i) => [name, i + 1])),
  },
  {
    name: "day of the week",
    min: 0,
    max: 7,
    names: new Map(WEEKDAYS.map((name, i) => [name, i])),
  },
];

function value(field: Field, text: string): number {
  const n = /^\d+$/.test(text) ? Number(text) : field.names?.get(text.toLowerCase());
  if (n === undefined || n < field.min || n > field.max)
    throw new CronError(
      `the ${field.name} "${text}" is not a number from ${field.min} to ${field.max}${field.names ? " or a name such as " + [...field.names.keys()].slice(0, 2).join(", ") : ""}`,
    );
  return n;
}

function values(field: Field, text: string): Set<number> {
  const found = new Set<number>();
  for (const item of text.split(",")) {
    const [range = "", step, extra] = item.split("/");
    if (extra !== undefined || range === "")
      throw new CronError(`the ${field.name} field "${text}" has an empty or malformed item`);
    let every = 1;
    if (step !== undefined) {
      if (!/^\d+$/.test(step) || Number(step) === 0)
        throw new CronError(`the step "${step}" of the ${field.name} is not a positive number`);
      every = Number(step);
    }
    let low: number;
    let high: number;
    if (range === "*") [low, high] = [field.min, field.max];
    else if (range.includes("-")) {
      const [from = "", to = "", more] = range.split("-");
      if (more !== undefined)
        throw new CronError(`the ${field.name} range "${range}" is malformed`);
      [low, high] = [value(field, from), value(field, to)];
      if (low > high) throw new CronError(`the ${field.name} range "${range}" runs backwards`);
    } else {
      if (step !== undefined)
        throw new CronError(
          `the ${field.name} "${item}" has a step without a range: write * or a range before /`,
        );
      low = high = value(field, range);
    }
    // Only the day of the week goes up to 7, which is Sunday again.
    for (let n = low; n <= high; n += every) found.add(field.max === 7 ? n % 7 : n);
  }
  return found;
}

/** Reads a cron expression; throws a CronError that says what is wrong. */
export function parseCron(source: string): CronExpression {
  const fields = source.trim().split(/\s+/).filter(Boolean);
  if (fields.length !== 5)
    throw new CronError(
      `"${source}" has ${fields.length} fields; a cron expression has five: minute, hour, day of the month, month, day of the week`,
    );
  const [minutes, hours, days, months, weekdays] = FIELDS.map((field, i) =>
    values(field, fields[i] ?? ""),
  ) as [Set<number>, Set<number>, Set<number>, Set<number>, Set<number>];
  return {
    source,
    minutes,
    hours,
    days,
    months,
    weekdays,
    starredDay: (fields[2] ?? "").startsWith("*") || (fields[4] ?? "").startsWith("*"),
  };
}

/** What is wrong with a cron expression, or `null` when it can be read. */
export function cronProblem(source: string): string | null {
  try {
    parseCron(source);
    return null;
  } catch (error) {
    if (error instanceof CronError) return error.message;
    throw error;
  }
}

/** Whether the expression names the minute of `date`, in local time. */
export function cronMatches(cron: CronExpression, date: Date): boolean {
  if (
    !cron.minutes.has(date.getMinutes()) ||
    !cron.hours.has(date.getHours()) ||
    !cron.months.has(date.getMonth() + 1)
  )
    return false;
  const day = cron.days.has(date.getDate());
  const weekday = cron.weekdays.has(date.getDay());
  return cron.starredDay ? day && weekday : day || weekday;
}
