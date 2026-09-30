/*
 * The schedules of alps-harness.yaml in the daemon. At the start of each minute (local time) it
 * wakes the agent of each schedule whose cron expression names that minute; a wake while another
 * runs is skipped and recorded by the harness. While schedules are configured it holds the server,
 * which then never stops when idle. The configuration is read again each minute, so edits apply
 * without a restart; while it cannot be read, the schedules it had stay.
 */

import { HarnessError, type Harness } from "../harness/index.ts";
import { cronMatches, parseCron, type CronExpression } from "../shared/cron.ts";

/** A local minute as `YYYY-MM-DDTHH:MM`, which sorts as time does. */
function minuteKey(date: Date): string {
  const two = (n: number): string => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${two(date.getMonth() + 1)}-${two(date.getDate())}T${two(date.getHours())}:${two(date.getMinutes())}`;
}

export interface Schedules {
  stop(): void;
}

export function startSchedules(options: {
  harness: Harness;
  /** Keeps the server from stopping when idle; the returned function lets it go. */
  hold: () => () => void;
  log: (line: string) => void;
}): Schedules {
  const { harness, log } = options;
  const parsed = new Map<string, CronExpression>();
  let schedules: { cron: string; agent: string }[] = [];
  let release: (() => void) | null = null;
  let timer: ReturnType<typeof setTimeout> | null = null;
  let stopped = false;
  // A daemon that starts in the middle of a minute wakes nobody for that minute.
  let done = minuteKey(new Date());

  const read = (): void => {
    const now = harness.schedules();
    if (now === null) return;
    schedules = now;
    if (schedules.length > 0) release ??= options.hold();
    else {
      release?.();
      release = null;
    }
  };

  const wake = (schedule: { cron: string; agent: string }): void => {
    harness.wake({ agent: schedule.agent }, { kind: "schedule", cron: schedule.cron }).then(
      (result) => {
        if (!result.skipped)
          log(
            `woke ${schedule.agent} by the schedule "${schedule.cron}": wake run ${result.run.id}`,
          );
      },
      (error: unknown) => {
        const message = error instanceof HarnessError ? error.message : String(error);
        log(`the schedule "${schedule.cron}" did not wake ${schedule.agent}: ${message}`);
      },
    );
  };

  const tick = (): void => {
    timer = null;
    if (stopped) return;
    const now = new Date();
    read();
    const key = minuteKey(now);
    // When the clock goes back (the end of daylight saving time), the minutes it repeats are skipped.
    if (key > done) {
      done = key;
      for (const schedule of schedules) {
        let cron = parsed.get(schedule.cron);
        if (!cron) {
          // The configuration's schema has checked the expression.
          cron = parseCron(schedule.cron);
          parsed.set(schedule.cron, cron);
        }
        if (cronMatches(cron, now)) wake(schedule);
      }
    }
    const next = new Date(now);
    next.setSeconds(60, 0);
    timer = setTimeout(tick, Math.max(1000, next.getTime() - now.getTime()) + 50);
  };

  read();
  const first = new Date();
  first.setSeconds(60, 0);
  timer = setTimeout(tick, first.getTime() - Date.now() + 50);

  return {
    stop() {
      stopped = true;
      if (timer) clearTimeout(timer);
      timer = null;
      release?.();
      release = null;
    },
  };
}
