<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import AppRail from './AppRail.svelte';
  import CommandPalette from './CommandPalette.svelte';
  let commandOpen = false;
  let ready = false;
  const metadata: Record<string, [string, string]> = {
    atlas: ['Atlas', 'Process and interface relationships'],
    runs: ['Runs', 'Current work and human attention'],
    library: ['Library', 'Skills, Plugins, and Process Models'],
    analysis: ['Analysis', 'Operational evidence for improvement']
  };
  $: key = $page.url.pathname.split('/')[1] || 'atlas';
  $: meta = metadata[key] ?? metadata.atlas;
  onMount(() => { ready = true; });
  function keydown(event: KeyboardEvent) {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      commandOpen = true;
    }
  }
</script>
<svelte:window on:keydown={keydown} />
<div class="app-shell" data-ready={ready ? 'true' : 'false'}>
  <AppRail />
  <main class="main-shell">
    <header class="topbar glass-soft">
      <div><h1>{meta[0]}</h1><p>{meta[1]}</p></div>
      <button class="command-trigger" aria-keyshortcuts="Control+K Meta+K" on:click={() => commandOpen = true}>Search or go to… <kbd>⌘K</kbd></button>
    </header>
    <div class="page-content"><slot /></div>
  </main>
</div>
<CommandPalette bind:open={commandOpen} />
