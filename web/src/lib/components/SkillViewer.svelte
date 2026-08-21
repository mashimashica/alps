<script lang="ts">
  import { Dialog } from 'bits-ui';
  import { createMutation, createQuery, useQueryClient } from '@tanstack/svelte-query';
  import { goto } from '$app/navigation';
  import { api, json } from '$lib/api';
  import type { AssetDetail, Run } from '$lib/types';
  import SafeMarkdown from './SafeMarkdown.svelte';
  import Badge from './ui/Badge.svelte';
  import Button from './ui/Button.svelte';
  export let open = false;
  export let assetId = '';
  const client = useQueryClient();
  let selectedPath = '';
  const detail = createQuery(() => ({
    queryKey: ['asset', assetId],
    queryFn: () => api<AssetDetail>(`/assets/${assetId}`),
    enabled: Boolean(open && assetId)
  }));
  $: if (detail.data && !selectedPath) selectedPath = detail.data.contentPath || detail.data.files?.[0] || '';
  const file = createQuery(() => ({
    queryKey: ['asset-content', assetId, selectedPath],
    queryFn: () => api<{ path: string; content: string }>(`/assets/${assetId}/content?path=${encodeURIComponent(selectedPath)}`),
    enabled: Boolean(open && assetId && selectedPath)
  }));
  const adopt = createMutation(() => ({
    mutationFn: () => api(`/assets/${assetId}/adopt`, json('POST', {})),
    onSuccess: async () => { await client.invalidateQueries({ queryKey: ['catalog'] }); await client.invalidateQueries({ queryKey: ['asset', assetId] }); }
  }));
  const start = createMutation(() => ({
    mutationFn: () => api<Run>('/runs', json('POST', { title: detail.data?.name, process: detail.data?.name, assetId })),
    onSuccess: async () => { open = false; await client.invalidateQueries({ queryKey: ['runs'] }); await goto('/runs'); }
  }));
  $: assetLabel = detail.data?.kind === 'plugin' ? 'Plugin' : detail.data?.kind === 'process-model' ? 'Model' : 'Skill';
  $: action = detail.data?.alpsState === 'adopted'
    ? detail.data?.kind === 'skill' ? 'Start Run' : 'Adopted'
    : detail.data?.alpsState === 'changed' ? 'Adopt New Revision'
    : detail.data?.validation === 'valid' ? `Adopt ${assetLabel}` : 'Review Validation';
  $: actionDisabled = adopt.isPending || start.isPending || (detail.data?.alpsState === 'adopted' && detail.data?.kind !== 'skill') || detail.data?.validation !== 'valid';
  function primary() { if (detail.data?.alpsState === 'adopted' && detail.data?.kind === 'skill') start.mutate(); else if (detail.data?.validation === 'valid') adopt.mutate(); }
  function close() { open = false; selectedPath = ''; }
</script>
<Dialog.Root bind:open onOpenChange={(value) => !value && close()}>
  <Dialog.Portal>
    <Dialog.Overlay class="dialog-overlay" />
    <Dialog.Content class="dialog-content skill-viewer" aria-label="Skill package viewer">
      {#if detail.isPending}<div class="empty-state">Loading Skill…</div>
      {:else if detail.isError}<div class="empty-state error">{detail.error.message}</div>
      {:else if detail.data}
        <header class="viewer-header">
          <div class="viewer-identity"><span class="asset-icon">{detail.data.kind === 'skill' ? 'S' : detail.data.kind === 'plugin' ? 'P' : 'M'}</span><div><h2>{detail.data.name}</h2><p>{detail.data.kind} · {detail.data.scope}</p></div></div>
          <button class="icon-close" on:click={close} aria-label="Close">×</button>
        </header>
        <div class="viewer-grid">
          <nav class="package-tree" aria-label="Package files">
            {#each detail.data.files ?? [] as path}<button class:active={path === selectedPath} on:click={() => selectedPath = path}>{path}</button>{/each}
          </nav>
          <article class="viewer-document">
            <div class="document-summary"><Badge tone={detail.data.validation === 'valid' ? 'success' : 'warning'}>{detail.data.validation}</Badge><p>{detail.data.description || 'No discovery description.'}</p></div>
            {#if selectedPath.toLowerCase().endsWith('.md')}<SafeMarkdown source={file.data?.content ?? detail.data.content ?? ''} />
            {:else}<pre class="raw-preview">{file.data?.content ?? detail.data.content ?? ''}</pre>{/if}
          </article>
        </div>
        <footer class="viewer-footer"><Button variant="primary" disabled={actionDisabled} on:click={primary}>{action}</Button></footer>
      {/if}
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
