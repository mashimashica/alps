/**
 * A deep copy, to give `toMatchObject` when the expectation has asymmetric matchers
 * (`expect.any`, `expect.stringMatching`): Bun 1.3.11 writes those matchers into the object it
 * checks, so the original would no longer hold its values afterwards.
 */
export const copyOf = <T>(value: T): T => structuredClone(value);
