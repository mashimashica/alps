<script lang="ts">
  import { Dialog } from 'bits-ui';
  import { createMutation, createQuery, useQueryClient } from '@tanstack/svelte-query';
  import { api, json } from '$lib/api';
  import type { Gate, Run } from '$lib/types';
  import { humanState, relativeTime } from '$lib/format';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import RunSheet from '$lib/components/RunSheet.svelte';
  let sheetOpen = false;
  let selectedRun = '';
  let createOpen = false;
  let title = '';
  let process = 'Apply Skills';
  const client = useQueryClient();
  const runs = createQuery(() => ({ queryKey: ['runs'], queryFn: () => api<Run[]>('/runs') }));
  const gates = createQuery(() => ({ queryKey: ['gates'], queryFn: () => api<Gate[]>('/gates') }));
  const createRun = createMutation(() => ({
    mutationFn: () => api<Run>('/runs', json('POST', { title, process })),
    onSuccess: async (run) => { createOpen = false; title = ''; await client.invalidateQueries({ queryKey: ['runs'] }); selectedRun = run.id; sheetOpen = true; }
  }));
  $: lanes = {
    Now: (runs.data ?? []).filter((run) => ['created', 'active'].includes(run.state)),
    Waiting: (runs.data ?? []).filter((run) => run.state.startsWith('waiting_') || run.state === 'completion_requested'),
    Done: (runs.data ?? []).filter((run) => ['completed', 'failed', 'cancelled'].includes(run.state))
  };
  function inspect(run: Run) { selectedRun = run.id; sheetOpen = true; }
  function openGate(run: Run) { return (gates.data ?? []).find((gate) => gate.runId === run.id); }
</script>
<svelte:head><title>Runs · ALPS Local Runtime</title></svelte:head>
<div class="page-actions"><Button variant="primary" on:click={() => createOpen = true}>Start Run</Button></div>
{#if runs.isPending}<div class="empty-state">Loading Runs…</div>
{:else if runs.isError}<div class="empty-state error">{runs.error.message}</div>
{:else}
  <div class="run-board">
    {#each Object.entries(lanes) as [lane, items]}
      <section class="run-lane"><header><h2>{lane}</h2><span>{items.length}</span></header><div class="run-cards">
        {#each items as run}
          <button class="run-card glass-soft" on:click={() => inspect(run)}>
            <h3>{run.title}</h3><p>{run.statusText || humanState(run.state)}</p>
            {#if run.progress != null}<progress value={run.progress} max="100"></progress>{/if}
            <footer>{#if openGate(run)}<Badge tone="danger">Decision</Badge>{:else}<span>{run.process}</span>{/if}<span>{relativeTime(run.updatedAt)}</span></footer>
          </button>
        {:else}<div class="lane-empty">No Runs</div>{/each}
      </div></section>
    {/each}
  </div>
{/if}
<RunSheet bind:open={sheetOpen} runId={selectedRun} />
<Dialog.Root bind:open={createOpen}>
  <Dialog.Portal><Dialog.Overlay class="dialog-overlay" /><Dialog.Content class="dialog-content form-dialog" aria-label="Start Run">
    <header><h2>Start Run</h2><button class="icon-close" on:click={() => createOpen = false} aria-label="Close">×</button></header>
    <label class="field"><span>Title</span><input bind:value={title} placeholder="Describe the work" /></label>
    <label class="field"><span>Process or Skill</span><input bind:value={process} /></label>
    {#if createRun.isError}<p class="form-error">{createRun.error.message}</p>{/if}
    <footer><Button on:click={() => createOpen = false}>Cancel</Button><Button variant="primary" disabled={!title.trim()} on:click={() => createRun.mutate()}>Start Run</Button></footer>
  </Dialog.Content></Dialog.Portal>
</Dialog.Root>
