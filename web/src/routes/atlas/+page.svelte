<script lang="ts">
  import { createQuery } from '@tanstack/svelte-query';
  import { api } from '$lib/api';
  import type { Graph } from '$lib/types';
  import AtlasCanvas from '$lib/components/AtlasCanvas.svelte';
  let mode: 'structure' | 'live' | 'flow' = 'structure';
  const graph = createQuery(() => ({
    queryKey: ['graph', mode],
    queryFn: () => api<Graph>(`/process-models/current/graph?mode=${mode}`)
  }));
</script>
<svelte:head><title>Atlas · ALPS Local Runtime</title></svelte:head>
{#if graph.isPending}<div class="empty-state">Resolving Process Model…</div>
{:else if graph.isError}<div class="empty-state error">{graph.error.message}</div>
{:else if graph.data}<AtlasCanvas graph={graph.data} {mode} onMode={(value) => mode = value} />{/if}
