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

Path("web/src/lib/format.test.ts").write_text("""import { describe, expect, it } from 'vitest';
import { humanState, number } from './format';

describe('format helpers', () => {
  it('preserves unavailable values', () => {
    expect(number(undefined)).toBe('—');
  });

  it('formats state identifiers for human display', () => {
    expect(humanState('waiting_for_decision')).toBe('waiting for decision');
  });
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

Path("web/src/lib/components/AppShell.svelte").write_text("""<script lang=\"ts\">
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
<div class=\"app-shell\" data-ready={ready ? 'true' : 'false'}>
  <AppRail />
  <main class=\"main-shell\">
    <header class=\"topbar glass-soft\">
      <div><h1>{meta[0]}</h1><p>{meta[1]}</p></div>
      <button class=\"command-trigger\" aria-keyshortcuts=\"Control+K Meta+K\" on:click={() => commandOpen = true}>Search or go to… <kbd>⌘K</kbd></button>
    </header>
    <div class=\"page-content\"><slot /></div>
  </main>
</div>
<CommandPalette bind:open={commandOpen} />
""")

Path("web/tests/navigation.spec.ts").write_text("""import { expect, test } from '@playwright/test';

test('primary routes and focused surfaces are available', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveURL(/\/atlas$/);
  await expect(page.getByRole('heading', { name: 'Atlas' })).toBeVisible();
  await page.getByRole('link', { name: 'Library' }).click();
  await expect(page.getByRole('heading', { name: 'Library' })).toBeVisible();
  await page.getByRole('link', { name: 'Runs' }).click();
  await expect(page.getByRole('heading', { name: 'Runs' })).toBeVisible();
  await page.getByRole('link', { name: 'Analysis' }).click();
  await expect(page.getByRole('heading', { name: 'Analysis' })).toBeVisible();
});

test('command palette opens from keyboard', async ({ page }) => {
  await page.goto('/atlas');
  await expect(page.locator('.app-shell')).toHaveAttribute('data-ready', 'true');
  await page.keyboard.press('Control+K');
  await expect(page.getByRole('dialog', { name: 'Command palette' })).toBeVisible();
});
""")

server = Path("internal/httpapi/server.go")
value = server.read_text()
old = "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
new = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
if old not in value:
    raise SystemExit('missing CSP correction pattern')
server.write_text(value.replace(old, new))
