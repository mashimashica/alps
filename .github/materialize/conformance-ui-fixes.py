from pathlib import Path

Path("web/vite.config.ts").write_text("""import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()]
});
""")

Path("web/vitest.config.ts").write_text("""import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: { include: ['src/**/*.test.ts'] }
});
""")

atlas = Path("web/src/lib/components/AtlasCanvas.svelte")
value = atlas.read_text()
value = value.replace(
    "function reset() { selected = ''; select(svg).transition().duration(180).call(zoomBehavior.transform, zoomIdentity); }",
    "function reset() { selected = ''; select(svg).call(zoomBehavior.transform, zoomIdentity); }",
)
atlas.write_text(value)

Path("web/src/lib/components/VirtualAssetList.svelte").write_text("""<script lang=\"ts\">
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
<div class=\"asset-scroll\" bind:this={scroller}>
  <div class=\"virtual-space\" style:height={`${$virtualizer.getTotalSize()}px`}>
    {#each $virtualizer.getVirtualItems() as row (row.key)}
      {@const asset = items[row.index]}
      <button class=\"asset-row virtual-row\" style:transform={`translateY(${row.start}px)`} on:click={() => onSelect(asset)}>
        <span class=\"asset-icon\">{asset.kind === 'skill' ? 'S' : asset.kind === 'plugin' ? 'P' : 'M'}</span>
        <span class=\"asset-copy\"><strong>{asset.name}</strong><small>{asset.kind} · {asset.scope}</small></span>
        <span class=\"asset-status\">{asset.alpsState === 'changed' ? 'Changed' : asset.alpsState === 'adopted' ? 'Adopted' : '›'}</span>
      </button>
    {/each}
  </div>
</div>
""")

palette = Path("web/src/lib/components/CommandPalette.svelte")
value = palette.read_text().replace(" autofocus />", " />")
palette.write_text(value)

test = Path("web/tests/navigation.spec.ts")
value = test.read_text().replace("process.platform === 'darwin' ? 'Meta+K' : 'Control+K'", "'Control+K'")
test.write_text(value)
