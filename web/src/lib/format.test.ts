import { describe, expect, it } from 'vitest';
import { humanState, number } from './format';

describe('format helpers', () => {
  it('preserves unavailable values', () => {
    expect(number(undefined)).toBe('—');
  });

  it('formats state identifiers for human display', () => {
    expect(humanState('waiting_for_decision')).toBe('waiting for decision');
  });
});
