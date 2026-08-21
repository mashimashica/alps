<script lang="ts">
  import { onMount } from 'svelte';
  import { select } from 'd3-selection';
  import { zoom, zoomIdentity, type ZoomTransform } from 'd3-zoom';
  import type { Graph, GraphNode } from '$lib/types';
  import Badge from './ui/Badge.svelte';
  export let graph: Graph;
  export let mode: 'structure' | 'live' | 'flow' = 'structure';
  export let onMode: (mode: 'structure' | 'live' | 'flow') => void;
  let svg: SVGSVGElement;
  let selected = '';
  let transform = zoomIdentity;
  const center = { x: 500, y: 330 };
  function radial(items: GraphNode[], radius: number) {
    return items.map((node, index) => {
      const angle = -Math.PI / 2 + index * Math.PI * 2 / Math.max(1, items.length);
      return { ...node, x: center.x + Math.cos(angle) * radius, y: center.y + Math.sin(angle) * radius };
    });
  }
  $: processes = radial(graph.processes ?? [], 250);
  $: interfaces = radial(graph.interfaces ?? [], 112);
  $: positioned = [...processes, ...interfaces];
  $: byId = new Map(positioned.map((item) => [item.id, item]));
  $: connected = selected ? new Set(graph.edges.filter((edge) => edge.from === selected || edge.to === selected).flatMap((edge) => [edge.from, edge.to])) : new Set<string>();
  $: selectedNode = positioned.find((item) => item.id === selected);
  function muted(id: string) { return Boolean(selected && id !== selected && !connected.has(id)); }
  function edgeMuted(from: string, to: string) { return Boolean(selected && from !== selected && to !== selected); }
  function reset() { selected = ''; select(svg).call(zoomBehavior.transform, zoomIdentity); }
  const zoomBehavior = zoom<SVGSVGElement, unknown>().scaleExtent([0.65, 2.8]).on('zoom', (event) => { transform = event.transform as ZoomTransform; });
  onMount(() => { select(svg).call(zoomBehavior); return () => select(svg).on('.zoom', null); });
</script>
<div class="atlas-toolbar segmented" role="tablist" aria-label="Atlas mode">
  {#each ['structure', 'live', 'flow'] as item}
    <button class:active={mode === item} on:click={() => onMode(item as typeof mode)}>{item[0].toUpperCase() + item.slice(1)}</button>
  {/each}
</div>
<div class="atlas-stage glass">
  <svg bind:this={svg} viewBox="0 0 1000 660" role="img" aria-label="Process Model network">
    <g transform={`translate(${transform.x} ${transform.y}) scale(${transform.k})`}>
      {#each graph.edges as edge}
        {@const from = byId.get(edge.from)}
        {@const to = byId.get(edge.to)}
        {#if from && to}
          <path class:muted={edgeMuted(edge.from, edge.to)} class="atlas-edge {edge.kind}" d={`M ${from.x} ${from.y} Q ${center.x} ${center.y} ${to.x} ${to.y}`}><title>{edge.kind}</title></path>
        {/if}
      {/each}
      {#each processes as node}
        <g class:muted={muted(node.id)} class:selected={selected === node.id} class="atlas-node process" transform={`translate(${node.x} ${node.y})`} role="button" tabindex="0" on:click={() => selected = node.id} on:keydown={(event) => event.key === 'Enter' && (selected = node.id)}>
          <circle r="34" /><text y="55">{node.name}</text>
        </g>
      {/each}
      {#each interfaces as node}
        <g class:muted={muted(node.id)} class:selected={selected === node.id} class="atlas-node interface" transform={`translate(${node.x} ${node.y})`} role="button" tabindex="0" on:click={() => selected = node.id} on:keydown={(event) => event.key === 'Enter' && (selected = node.id)}>
          <circle r="25" /><text y="4">{node.name.length > 15 ? `${node.name.slice(0, 14)}…` : node.name}</text>
        </g>
      {/each}
      {#if mode !== 'structure'}
        {#each graph.live ?? [] as item}
          {@const node = byId.get(item.processId)}
          {#if node}<circle class:attention={item.attention} class="live-dot" cx={node.x + 24} cy={node.y - 24} r="7"><title>{item.state}</title></circle>{/if}
        {/each}
      {/if}
      {#if mode === 'flow'}
        {#each graph.flow ?? [] as item}
          {@const node = byId.get(item.interfaceId ?? item.from ?? '')}
          {#if node}<circle class="flow-dot" cx={node.x} cy={node.y - 34} r="5"><title>{item.status}</title></circle>{/if}
        {/each}
      {/if}
    </g>
  </svg>
  <button class="atlas-mark" on:click={reset} aria-label="Reset Atlas view"><img src="/assets/icon.svg" alt="ALPS" /></button>
  {#if selectedNode}
    <aside class="atlas-inspector glass-soft">
      <Badge tone={selectedNode.kind === 'process' ? 'info' : 'neutral'}>{selectedNode.kind}</Badge>
      <h2>{selectedNode.name}</h2>
      {#if selectedNode.revisionId}<p>Revision {selectedNode.revisionId}</p>{/if}
      <p>{connected.size - 1} connected element{connected.size - 1 === 1 ? '' : 's'}</p>
      <button class="icon-close" on:click={() => selected = ''} aria-label="Close inspector">×</button>
    </aside>
  {/if}
</div>
