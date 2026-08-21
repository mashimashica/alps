<script lang="ts">
  import { createQuery } from '@tanstack/svelte-query';
  import { api } from '$lib/api';
  import type { Asset } from '$lib/types';
  import VirtualAssetList from '$lib/components/VirtualAssetList.svelte';
  import SkillViewer from '$lib/components/SkillViewer.svelte';
  let search = '';
  let filter = 'all';
  let viewerOpen = false;
  let assetId = '';
  const catalog = createQuery(() => ({ queryKey: ['catalog'], queryFn: () => api<Asset[]>('/catalog') }));
  $: items = (catalog.data ?? []).filter((asset) => (filter === 'all' || asset.kind === filter) && (!search || `${asset.name} ${asset.description}`.toLowerCase().includes(search.toLowerCase())));
  function inspect(asset: Asset) { assetId = asset.id; viewerOpen = true; }
</script>
<svelte:head><title>Library · ALPS Local Runtime</title></svelte:head>
<section class="panel glass library-panel">
  <div class="library-toolbar">
    <input bind:value={search} class="search-input" placeholder="Search Skills, Plugins, and Models" aria-label="Search assets" />
    <div class="segmented" role="tablist">{#each [['all','All'],['skill','Skills'],['plugin','Plugins'],['process-model','Models']] as item}<button class:active={filter === item[0]} on:click={() => filter = item[0]}>{item[1]}</button>{/each}</div>
  </div>
  {#if catalog.isPending}<div class="empty-state">Discovering assets…</div>
  {:else if catalog.isError}<div class="empty-state error">{catalog.error.message}</div>
  {:else}<VirtualAssetList {items} onSelect={inspect} />{/if}
</section>
<SkillViewer bind:open={viewerOpen} {assetId} />
