<script lang="ts">
  import { Dialog } from 'bits-ui';
  import { createMutation, useQueryClient } from '@tanstack/svelte-query';
  import { api, json } from '$lib/api';
  import type { Gate, Run } from '$lib/types';
  import Badge from './ui/Badge.svelte';
  import Button from './ui/Button.svelte';
  export let open = false;
  export let gate: Gate | undefined;
  export let run: Run | undefined;
  export let afterDecision: () => void = () => undefined;
  const client = useQueryClient();
  let rationale = '';
  const mutation = createMutation(() => ({
    mutationFn: (decision: string) => api(`/gates/${gate?.id}/decisions`, json('POST', {
      decision,
      actor: 'local-user',
      authority: 'operator',
      rationale,
      expectedVersion: run?.version
    })),
    onSuccess: async () => {
      await client.invalidateQueries({ queryKey: ['runs'] });
      await client.invalidateQueries({ queryKey: ['gates'] });
      if (run?.id) await client.invalidateQueries({ queryKey: ['run', run.id] });
      open = false;
      rationale = '';
      afterDecision();
    }
  }));
  function act(decision: string) { mutation.mutate(decision); }
</script>
<Dialog.Root bind:open>
  <Dialog.Portal>
    <Dialog.Overlay class="dialog-overlay" />
    <Dialog.Content class="dialog-content decision-dialog" aria-label="Human Decision">
      {#if gate && run}
        <header class="decision-header"><Badge tone="danger">Human decision</Badge><button class="icon-close" on:click={() => open = false} aria-label="Close">×</button></header>
        <h2>{gate.title}</h2>
        <p class="decision-effect">{gate.effect}</p>
        <dl class="decision-facts">
          <div><dt>Run</dt><dd>{run.title} · version {run.version}</dd></div>
          <div><dt>External effect</dt><dd>{gate.externalEffect || 'No external effect was declared.'}</dd></div>
          <div><dt>Reversibility</dt><dd>{gate.reversible ? 'Reversible' : 'Irreversible'}</dd></div>
          <div><dt>Authority</dt><dd>{gate.authority}</dd></div>
        </dl>
        {#if gate.criteria?.length}<section class="decision-list"><h3>Criteria</h3><ul>{#each gate.criteria as item}<li>{item}</li>{/each}</ul></section>{/if}
        {#if gate.unknown?.length}<section class="decision-list warning"><h3>Unknown</h3><ul>{#each gate.unknown as item}<li>{item}</li>{/each}</ul></section>{/if}
        {#if gate.evidence?.length}<section class="decision-list"><h3>Evidence</h3><ul>{#each gate.evidence as item}<li>{item.description || item.id || item.uri || item.digest}</li>{/each}</ul></section>{/if}
        <label class="field"><span>Rationale</span><textarea bind:value={rationale} rows="3" placeholder="Record the basis for the Decision"></textarea></label>
        {#if mutation.isError}<p class="form-error">{mutation.error.message}</p>{/if}
        <footer class="decision-actions">
          <Button on:click={() => act('hold')}>Hold</Button>
          <Button on:click={() => act('change')}>Return for changes</Button>
          <Button variant="primary" on:click={() => act('continue')}>Continue</Button>
        </footer>
      {/if}
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
