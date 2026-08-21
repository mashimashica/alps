export function relativeTime(value?: string): string {
  if (!value) return '';
  const seconds = Math.max(0, Math.floor((Date.now() - Date.parse(value)) / 1000));
  if (seconds < 60) return 'now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
  return `${Math.floor(seconds / 86400)}d`;
}
export function number(value: unknown): string {
  return typeof value === 'number' ? new Intl.NumberFormat().format(value) : value == null ? '—' : String(value);
}
export function humanState(value: string): string { return value.replaceAll('_', ' '); }
