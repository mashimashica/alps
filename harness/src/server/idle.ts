/** setTimeout cannot wait longer than 2^31 - 1 ms. */
const MAX_DELAY_MS = 2 ** 31 - 1;

/**
 * Calls `onIdle` once nothing has happened for `idleMs`. Every request resets the wait;
 * a hold (an open event stream, a running run) suspends it until released.
 * With `idleMs` null the tracker never fires (the daemon has schedules).
 */
export class IdleTracker {
  #holds = 0;
  #timer: ReturnType<typeof setTimeout> | null = null;
  #stopped = false;
  readonly #idleMs: number | null;
  readonly #onIdle: () => void;

  constructor(idleMs: number | null, onIdle: () => void) {
    this.#idleMs = idleMs === null ? null : Math.min(Math.max(1, Math.round(idleMs)), MAX_DELAY_MS);
    this.#onIdle = onIdle;
  }

  start(): void {
    this.#arm();
  }

  touch(): void {
    if (this.#holds === 0) this.#arm();
  }

  /** Suspends the wait until the returned function is called. Calling it twice releases once. */
  hold(): () => void {
    this.#holds += 1;
    this.#disarm();
    let released = false;
    return () => {
      if (released) return;
      released = true;
      this.#holds -= 1;
      if (this.#holds === 0) this.#arm();
    };
  }

  stop(): void {
    this.#stopped = true;
    this.#disarm();
  }

  #arm(): void {
    this.#disarm();
    if (this.#stopped || this.#idleMs === null) return;
    this.#timer = setTimeout(() => {
      this.#timer = null;
      if (!this.#stopped && this.#holds === 0) this.#onIdle();
    }, this.#idleMs);
  }

  #disarm(): void {
    if (this.#timer) clearTimeout(this.#timer);
    this.#timer = null;
  }
}
