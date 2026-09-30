/* Cron expressions of schedules (Scheduled runs): the five fields of crontab(5), in local time. */

import { describe, expect, test } from "bun:test";
import { cronMatches, cronProblem, parseCron } from "../../src/shared/cron.ts";

/** A local date and time: year, month (1 to 12), day, hour, minute. */
const at = (year: number, month: number, day: number, hour: number, minute: number): Date =>
  new Date(year, month - 1, day, hour, minute);

const matches = (expression: string, date: Date): boolean =>
  cronMatches(parseCron(expression), date);

/** The minutes of one local day that an expression names, as HH:MM. */
function minutesOf(expression: string, year: number, month: number, day: number): string[] {
  const cron = parseCron(expression);
  const found: string[] = [];
  for (let minute = 0; minute < 24 * 60; minute++) {
    const date = at(year, month, day, Math.floor(minute / 60), minute % 60);
    if (cronMatches(cron, date))
      found.push(
        `${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`,
      );
  }
  return found;
}

describe("cron expressions", () => {
  test("the five fields name the minute, hour, day of the month, month, and day of the week", () => {
    // 2026-09-28 is a Monday.
    expect(minutesOf("0 9 * * 1-5", 2026, 9, 28)).toEqual(["09:00"]);
    expect(minutesOf("0 9 * * 1-5", 2026, 9, 27)).toEqual([]);
    expect(minutesOf("30 8,12 * * *", 2026, 9, 27)).toEqual(["08:30", "12:30"]);
    expect(minutesOf("*/20 9-10 * * *", 2026, 9, 27)).toEqual([
      "09:00",
      "09:20",
      "09:40",
      "10:00",
      "10:20",
      "10:40",
    ]);
    expect(minutesOf("15 9-17/4 * * *", 2026, 9, 27)).toEqual(["09:15", "13:15", "17:15"]);
    expect(matches("0 0 1 1 *", at(2027, 1, 1, 0, 0))).toBe(true);
    expect(matches("0 0 1 1 *", at(2027, 1, 2, 0, 0))).toBe(false);
    expect(matches("* * * * *", at(2026, 9, 30, 23, 59))).toBe(true);
  });

  test("months and days of the week can be named, and 0 and 7 are both Sunday", () => {
    // 2026-09-27 is a Sunday.
    expect(matches("0 12 * sep sun", at(2026, 9, 27, 12, 0))).toBe(true);
    expect(matches("0 12 * SEP Sun", at(2026, 9, 27, 12, 0))).toBe(true);
    expect(matches("0 12 * * 7", at(2026, 9, 27, 12, 0))).toBe(true);
    expect(matches("0 12 * * 0", at(2026, 9, 27, 12, 0))).toBe(true);
    expect(matches("0 12 * * mon-fri", at(2026, 9, 27, 12, 0))).toBe(false);
    expect(matches("0 12 * jan-mar *", at(2026, 9, 27, 12, 0))).toBe(false);
  });

  test("a day matches either restricted day field, but both when one of them starts with *", () => {
    // 2026-10-01 is a Thursday, 2026-10-05 a Monday, 2026-10-13 a Tuesday.
    expect(matches("0 9 1 * mon", at(2026, 10, 1, 9, 0))).toBe(true);
    expect(matches("0 9 1 * mon", at(2026, 10, 5, 9, 0))).toBe(true);
    expect(matches("0 9 1 * mon", at(2026, 10, 13, 9, 0))).toBe(false);
    // With a starred day field (a step included), the other one must match too.
    expect(matches("0 9 */2 * mon", at(2026, 10, 5, 9, 0))).toBe(true);
    expect(matches("0 9 */2 * mon", at(2026, 10, 13, 9, 0))).toBe(false);
    expect(matches("0 9 */2 * mon", at(2026, 10, 1, 9, 0))).toBe(false);
  });

  test("an expression that is not five readable fields is refused with what is wrong", () => {
    expect(cronProblem("0 9 * * 1-5")).toBeNull();
    const cases: [string, RegExp][] = [
      ["0 9 * *", /has 4 fields; a cron expression has five/],
      ["@daily", /has 1 fields/],
      ["60 * * * *", /minute "60" is not a number from 0 to 59/],
      ["* 24 * * *", /hour "24" is not a number from 0 to 23/],
      ["* * 0 * *", /day of the month "0" is not a number from 1 to 31/],
      ["* * * 13 *", /month "13" is not a number from 1 to 12 or a name/],
      ["* * * * 8", /day of the week "8" is not a number from 0 to 7/],
      // Names are those of months and days only, not the properties every object inherits.
      ["0 9 * constructor *", /month "constructor" is not a number from 1 to 12 or a name/],
      ["0 9 * * __proto__", /day of the week "__proto__" is not a number from 0 to 7 or a name/],
      ["* * * * mon-sun", /range "mon-sun" runs backwards/],
      ["*/0 * * * *", /step "0" of the minute is not a positive number/],
      ["5/15 * * * *", /step without a range/],
      ["1,,2 * * * *", /empty or malformed item/],
      ["1-2-3 * * * *", /range "1-2-3" is malformed/],
    ];
    for (const [expression, message] of cases)
      expect(cronProblem(expression), expression).toMatch(message);
  });
});
