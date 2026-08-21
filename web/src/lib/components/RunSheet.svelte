<script lang="ts">
  import { Dialog } from 'bits-ui';
  import { createQuery } from '@tanstack/svelte-query';
  import { api } from '$lib/api';
  import type { RunDetail } from '$lib/types';
  import { humanState, number, relativeTime } from '$lib/format';
  import Badge from './ui/Badge.svelte';
  import DecisionDialog from './DecisionDialog.svelte';
  export let open = false;
  export let runId = '';
  let decisionOpen = false;
  const detail = createQuery(() => ({
    queryKey: ['run', runId],
    queryFn: () => api<RunDetail>(`/runs/${runId}`),
    enabled: Boolean(open && runId)
  }));
  function outcomeTone(status: string) { return status === 'assessed_achieved' ? 'success' : status === 'not_achieved' ? 'danger' : status === 'agent_reported' ? 'info' : 'neutral'; }
</script>
<Dialog.Root bind:open>
  <Dialog.Portal>
    <Dialog.Overlay class="dialog-overlay" />
    <Dialog.Content class="dialog-content run-sheet" aria-label="Run detail">
      {#if detail.isPending}<div class="empty-state">Loading Run…</div>
      {:else if detail.isError}<div class="empty-state error">{detail.error.message}</div>
      {:else if detail.data}
        <header class="viewer-header">
          <div class="viewer-identity"><span class="asset-icon">R</span><div><h2>{detail.data.run.title}</h2><p>{detail.data.run.process} · {humanState(detail.data.run.state)}</p></div></div>
          <button class="icon-close" on:click={() => open = false} aria-label="Close">×</button>
        </header>
        <div class="run-sheet-content">
          {#if detail.data.gate}<button class="attention-action" on:click={() => decisionOpen = true}><span>Decision required</span><strong>{detail.data.gate.title}</strong></button>{/if}
          <section class="run-section"><h3>Outcomes</h3>
            {#if detail.data.outcomes?.length}<div class="outcome-list">{#each detail.data.outcomes as outcome}<div><Badge tone={outcomeTone(outcome.status)}>{humanState(outcome.status)}</Badge><span>{outcome.name}</span></div>{/each}</div>{:else}<p class="muted">No Outcomes were declared for this Run.</p>{/if}
          </section>
          <section class="run-section"><h3>Effective context</h3><dl class="context-grid"><div><dt>Process revision</dt><dd>{detail.data.run.processRevisionId || '—'}</dd></div><div><dt>Skill package</dt><dd>{detail.data.run.skillPackageRevisionId || '—'}</dd></div><div><dt>Process Model</dt><dd>{detail.data.run.processModelRevisionId || '—'}</dd></div><div><dt>Actor</dt><dd>{detail.data.run.actor?.type || 'system'} · {detail.data.run.actor?.channel || 'internal'}</dd></div></dl></section>
          <section class="run-section"><h3>Artifacts and Handoffs</h3><div class="compact-list">{#each detail.data.artifacts ?? [] as artifact}<div><strong>{artifact.name}</strong><span>{artifact.role || artifact.mediaType} · {number(artifact.size)} bytes</span></div>{/each}{#each detail.data.handoffs ?? [] as handoff}<div><strong>Handoff</strong><span>{String(handoff.status ?? '')} · {String(handoff.recipientInput ?? '')}</span></div>{/each}{#if !(detail.data.artifacts?.length || detail.data.handoffs?.length)}<p class="muted">No Artifacts or Handoffs.</p>{/if}</div></section>
          <section class="run-section"><h3>Model and usage</h3><div class="compact-list">{#each detail.data.modelInvocations ?? [] as invocation}<div><strong>{String((invocation.resolved as Record<string, unknown>)?.modelRaw ?? (invocation.requested as Record<string, unknown>)?.modelRaw ?? 'Model invocation')}</strong><span>{String(invocation.role ?? 'main')}</span></div>{/each}{#each detail.data.usageObservations ?? [] as observation}<div><strong>{String(observation.status ?? 'usage')}</strong><span>{String(observation.accountingBasis ?? observation.source ?? 'reported')}</span></div>{/each}{#if !(detail.data.modelInvocations?.length || detail.data.usageObservations?.length)}<p class="muted">No model usage was reported.</p>{/if}</div></section>
          <section class="run-section"><h3>Timeline</h3><div class="timeline">{#each detail.data.events ?? [] as event}<div><span class="event-dot"></span><div><strong>{event.eventType}</strong><small>{relativeTime(event.occurredAt)}</small></div></div>{/each}</div></section>
        </div>
        <DecisionDialog bind:open={decisionOpen} gate={detail.data.gate} run={detail.data.run} afterDecision={() => detail.refetch()} />
      {/if}
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
