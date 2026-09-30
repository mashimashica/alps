/*
 * The dashboard's trend charts, drawn as SVG: stacked bars (with an optional rate line), lines,
 * and dots with whiskers. Each bucket can be clicked to list what it counts.
 */

import { fx } from "../graph/geometry.ts";

const W = 560;
const H = 150;
const PAD = { left: 38, right: 38, top: 12, bottom: 24 };
const PLOT_W = W - PAD.left - PAD.right;
const PLOT_H = H - PAD.top - PAD.bottom;

export interface SeriesStyle {
  label: string;
  /** The CSS class that colours it. */
  className: string;
}

interface Frame {
  labels: readonly string[];
  /** The title of each bucket (its date and values), for the tooltip and assistive technology. */
  titles: readonly string[];
  onPick?: (index: number) => void;
}

const slotWidth = (n: number): number => PLOT_W / Math.max(1, n);
const centerOf = (i: number, n: number): number => PAD.left + slotWidth(n) * (i + 0.5);
const yOf = (value: number, max: number): number =>
  PAD.top + PLOT_H - (max > 0 ? (value / max) * PLOT_H : 0);

/** A round maximum for an axis. */
function niceMax(value: number): number {
  if (value <= 0) return 1;
  const magnitude = 10 ** Math.floor(Math.log10(value));
  const step = [1, 2, 2.5, 5, 10].find((s) => s * magnitude >= value) ?? 10;
  return step * magnitude;
}

/** The x labels: at most six, evenly apart. */
function XLabels({ labels }: { labels: readonly string[] }) {
  const n = labels.length;
  const every = Math.max(1, Math.ceil(n / 6));
  return (
    <g class="axis">
      <line x1={PAD.left} y1={PAD.top + PLOT_H} x2={W - PAD.right} y2={PAD.top + PLOT_H} />
      {labels.map((label, i) =>
        i % every === 0 || i === n - 1 ? (
          <text key={i} x={fx(centerOf(i, n))} y={H - 6} text-anchor="middle">
            {label}
          </text>
        ) : null,
      )}
    </g>
  );
}

function YLabel({
  max,
  format,
  right,
}: {
  max: number;
  format: (v: number) => string;
  right?: boolean;
}) {
  const x = right ? W - PAD.right + 6 : PAD.left - 6;
  const anchor = right ? "start" : "end";
  return (
    <g class="axis">
      <text x={x} y={PAD.top + 4} text-anchor={anchor}>
        {format(max)}
      </text>
      <text x={x} y={PAD.top + PLOT_H} text-anchor={anchor}>
        {format(0)}
      </text>
    </g>
  );
}

/** Transparent slots over the buckets, which a click picks. */
function Slots({ labels, titles, onPick }: Frame) {
  const n = labels.length;
  const width = slotWidth(n);
  return (
    <g class="slots">
      {labels.map((_, i) => (
        <rect
          key={i}
          class={onPick ? "slot pickable" : "slot"}
          x={fx(PAD.left + width * i)}
          y={PAD.top}
          width={fx(width)}
          height={PLOT_H}
          onClick={onPick ? () => onPick(i) : undefined}
        >
          <title>{titles[i]}</title>
        </rect>
      ))}
    </g>
  );
}

export function Legend({ series }: { series: readonly SeriesStyle[] }) {
  return (
    <div class="chart-legend">
      {series.map((s) => (
        <span key={s.label}>
          <span class={`swatch ${s.className}`} />
          {s.label}
        </span>
      ))}
    </div>
  );
}

/** Stacked bars per bucket, with an optional line of a rate (0 to 1) on its own axis. */
export function StackedBars({
  labels,
  titles,
  onPick,
  stacks,
  series,
  rate,
}: Frame & {
  stacks: readonly (readonly number[])[];
  series: readonly SeriesStyle[];
  rate?: readonly (number | null)[];
}) {
  const n = labels.length;
  const max = niceMax(Math.max(0, ...stacks.map((values) => values.reduce((a, b) => a + b, 0))));
  const bar = Math.min(22, slotWidth(n) * 0.7);
  const segments: string[] = [];
  if (rate) {
    let open = false;
    rate.forEach((value, i) => {
      if (value === null) {
        open = false;
        return;
      }
      segments.push(`${open ? "L" : "M"}${fx(centerOf(i, n))} ${fx(yOf(value, 1))}`);
      open = true;
    });
  }
  return (
    <svg class="chart" viewBox={`0 0 ${W} ${H}`} role="img">
      <YLabel max={max} format={(v) => String(v)} />
      {rate && <YLabel max={1} format={(v) => `${Math.round(v * 100)}%`} right />}
      <XLabels labels={labels} />
      {stacks.map((values, i) => {
        let top = PAD.top + PLOT_H;
        return (
          <g key={i}>
            {values.map((value, k) => {
              if (value <= 0) return null;
              const height = (value / max) * PLOT_H;
              top -= height;
              return (
                <rect
                  key={k}
                  class={series[k]?.className}
                  x={fx(centerOf(i, n) - bar / 2)}
                  y={fx(top)}
                  width={fx(bar)}
                  height={fx(height)}
                />
              );
            })}
          </g>
        );
      })}
      {rate && <path class="rate-line" d={segments.join("")} />}
      {rate?.map((value, i) =>
        value === null ? null : (
          <circle key={i} class="rate-dot" cx={fx(centerOf(i, n))} cy={fx(yOf(value, 1))} r={2.5} />
        ),
      )}
      <Slots labels={labels} titles={titles} onPick={onPick} />
    </svg>
  );
}

/** A line per series. */
export function Lines({
  labels,
  titles,
  onPick,
  series,
  values,
  format,
}: Frame & {
  series: readonly SeriesStyle[];
  values: readonly (readonly (number | null)[])[];
  format: (v: number) => string;
}) {
  const n = labels.length;
  const max = niceMax(Math.max(0, ...values.flat().map((v) => v ?? 0)));
  return (
    <svg class="chart" viewBox={`0 0 ${W} ${H}`} role="img">
      <YLabel max={max} format={format} />
      <XLabels labels={labels} />
      {series.map((s, k) => {
        let open = false;
        const d = (values[k] ?? [])
          .map((value, i) => {
            if (value === null) {
              open = false;
              return "";
            }
            const part = `${open ? "L" : "M"}${fx(centerOf(i, n))} ${fx(yOf(value, max))}`;
            open = true;
            return part;
          })
          .join("");
        return (
          <g key={s.label}>
            <path class={`series-line ${s.className}`} d={d} />
            {(values[k] ?? []).map((value, i) =>
              value === null ? null : (
                <circle
                  key={i}
                  class={`series-dot ${s.className}`}
                  cx={fx(centerOf(i, n))}
                  cy={fx(yOf(value, max))}
                  r={2.5}
                />
              ),
            )}
          </g>
        );
      })}
      <Slots labels={labels} titles={titles} onPick={onPick} />
    </svg>
  );
}

/** A dot at each median, and a whisker from it to the p90. */
export function Whiskers({
  labels,
  titles,
  onPick,
  medians,
  p90s,
  format,
}: Frame & {
  medians: readonly (number | null)[];
  p90s: readonly (number | null)[];
  format: (v: number) => string;
}) {
  const n = labels.length;
  const max = niceMax(Math.max(0, ...p90s.map((v) => v ?? 0), ...medians.map((v) => v ?? 0)));
  return (
    <svg class="chart" viewBox={`0 0 ${W} ${H}`} role="img">
      <YLabel max={max} format={format} />
      <XLabels labels={labels} />
      {medians.map((median, i) => {
        if (median === null) return null;
        const x = fx(centerOf(i, n));
        const p90 = p90s[i] ?? median;
        return (
          <g key={i}>
            <line class="whisker" x1={x} y1={fx(yOf(median, max))} x2={x} y2={fx(yOf(p90, max))} />
            <line
              class="whisker"
              x1={fx(centerOf(i, n) - 4)}
              y1={fx(yOf(p90, max))}
              x2={fx(centerOf(i, n) + 4)}
              y2={fx(yOf(p90, max))}
            />
            <circle class="median" cx={x} cy={fx(yOf(median, max))} r={3.5} />
          </g>
        );
      })}
      <Slots labels={labels} titles={titles} onPick={onPick} />
    </svg>
  );
}
