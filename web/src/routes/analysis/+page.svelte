<script lang="ts">
  import { createQuery } from '@tanstack/svelte-query';
  import { api } from '$lib/api';
  import type { AnalysisLens } from '$lib/types';
  import { number } from '$lib/format';
  import Badge from '$lib/components/ui/Badge.svelte';
  let lens: 'flow' | 'quality' | 'oversight' | 'usage' = 'flow';
  const analysis = createQuery(() => ({ queryKey: ['analysis', lens], queryFn: () => api<AnalysisLens>(`/analysis/${lens}`) }));
  function maxValue(points: Array<{ value: number }>) { return Math.max(1, ...points.map((point) => point.value)); }
</script>
<svelte:head><title>Analysis · ALPS Local Runtime</title></svelte:head>
<div class="analysis-tabs segmented">{#each ['flow','quality','oversight','usage'] as item}<button class:active={lens === item} on:click={() => lens = item as typeof lens}>{item[0].toUpperCase() + item.slice(1)}</button>{/each}</div>
{#if analysis.isPending}<div class="empty-state">Building analytical projection…</div>
{:else if analysis.isError}<div class="empty-state error">{analysis.error.message}</div>
{:else if analysis.data}
  <section class="analysis-layout">
    <div class="metric-grid">{#each analysis.data.metrics.slice(0,3) as metric}<article class="metric-card glass"><strong>{number(metric.value)}</strong><h2>{metric.label}</h2><p>{metric.definition}</p><small>{metric.coverage}</small></article>{/each}</div>
    <article class="analysis-chart panel glass"><header><div><h2>{analysis.data.lens} over time</h2><p>{analysis.data.definition}</p></div><Badge tone="neutral">{analysis.data.mappingRevision}</Badge></header>
      {#if analysis.data.series?.[0]?.points?.length}
        {@const series = analysis.data.series[0]}{@const maximum = maxValue(series.points)}
        <div class="bars" aria-label={series.label}>{#each series.points as point}<div class="bar-column" title={`${point.at}: ${point.value}`}><div class="bar" style:height={`${Math.max(3, point.value / maximum * 100)}%`}></div><span>{point.at.slice(5,10)}</span></div>{/each}</div>
      {:else}<div class="empty-state compact">No time series is available for this period.</div>{/if}
    </article>
    <article class="findings panel glass"><h2>Findings</h2>{#each analysis.data.findings.slice(0,3) as finding}<div class="finding"><Badge tone={finding.severity === 'warning' ? 'warning' : finding.severity === 'error' ? 'danger' : 'info'}>{finding.severity}</Badge><div><strong>{finding.title}</strong><p>{finding.detail}</p></div></div>{:else}<p class="muted">No actionable finding in the selected lens.</p>{/each}</article>
  </section>
{/if}
