import type { QueryClient } from '@tanstack/svelte-query';

const eventGroups: Record<string, readonly unknown[][]> = {
  'catalog.scanned': [['catalog'], ['models'], ['graph']],
  'asset.adopted': [['catalog'], ['models'], ['graph']],
  'run.created': [['runs'], ['analysis'], ['graph']],
  'run.reported': [['runs'], ['run'], ['analysis'], ['graph']],
  'run.completion_requested': [['runs'], ['run'], ['analysis']],
  'run.completed': [['runs'], ['run'], ['analysis'], ['graph']],
  'gate.opened': [['runs'], ['gates'], ['run'], ['analysis'], ['graph']],
  'decision.recorded': [['runs'], ['gates'], ['run'], ['analysis'], ['graph']],
  'assessment.recorded': [['run'], ['analysis']],
  'handoff.created': [['run'], ['analysis'], ['graph']],
  'handoff.updated': [['run'], ['analysis'], ['graph']],
  'artifact.committed': [['run'], ['analysis'], ['graph']],
  'usage.observed': [['run'], ['analysis']],
  'cost.observed': [['run'], ['analysis']],
  'host.observed': [['run'], ['analysis']]
};

export function connectRealtime(client: QueryClient): () => void {
  const source = new EventSource('/v1/events/stream');
  for (const [type, keys] of Object.entries(eventGroups)) {
    source.addEventListener(type, (event) => {
      let streamId = '';
      try { streamId = JSON.parse((event as MessageEvent).data).streamId ?? ''; } catch { /* ignore */ }
      for (const key of keys) {
        const queryKey = key[0] === 'run' && streamId ? ['run', streamId] : key;
        void client.invalidateQueries({ queryKey });
      }
    });
  }
  return () => source.close();
}
