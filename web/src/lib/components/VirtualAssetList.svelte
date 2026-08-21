<script lang="ts">
  import { createVirtualizer } from '@tanstack/svelte-virtual';
  import type { Asset } from '$lib/types';
  export let items: Asset[] = [];
  export let onSelect: (asset: Asset) => void;
  let scroller: HTMLDivElement;
  $: virtualizer = createVirtualizer<HTMLDivElement, HTMLDivElement>({
    count: items.length,
    getScrollElement: () => scroller,
    estimateSize: () => 66,
    overscan: 8
  });
</script>
<div class="asset-scroll" bind:this={scroller}>
  <div class="virtual-space" style:height={`${$virtualizer.getTotalSize()}px`}>
    {#each $virtualizer.getVirtualItems() as row (row.key)}
      {@const asset = items[row.index]}
      <button class="asset-row virtual-row" style:transform={`translateY(${row.start}px)`} on:click={() => onSelect(asset)}>
        <span class="asset-icon">{asset.kind === 'skill' ? 'S' : asset.kind === 'plugin' ? 'P' : 'M'}</span>
        <span class="asset-copy"><strong>{asset.name}</strong><small>{asset.kind} · {asset.scope}</small></span>
        <span class="asset-status">{asset.alpsState === 'changed' ? 'Changed' : asset.alpsState === 'adopted' ? 'Adopted' : '›'}</span>
      </button>
    {/each}
  </div>
</div>
