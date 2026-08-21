<script lang="ts">
  import { goto } from '$app/navigation';
  import { Dialog } from 'bits-ui';
  export let open = false;
  const routes = [
    { href: '/atlas', name: 'Atlas', detail: 'Process and interface structure' },
    { href: '/runs', name: 'Runs', detail: 'Work and human attention' },
    { href: '/library', name: 'Library', detail: 'Skills, Plugins, and Models' },
    { href: '/analysis', name: 'Analysis', detail: 'Flow, quality, oversight, and usage' }
  ];
  let search = '';
  $: visible = routes.filter((item) => `${item.name} ${item.detail}`.toLowerCase().includes(search.toLowerCase()));
  function select(href: string) { open = false; search = ''; void goto(href); }
</script>
<Dialog.Root bind:open>
  <Dialog.Portal>
    <Dialog.Overlay class="dialog-overlay" />
    <Dialog.Content class="dialog-content command-dialog" aria-label="Command palette">
      <input class="command-input" bind:value={search} placeholder="Search or go to…" />
      <div class="command-results">
        {#each visible as item}
          <button class="command-item" on:click={() => select(item.href)}><strong>{item.name}</strong><span>{item.detail}</span></button>
        {/each}
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
