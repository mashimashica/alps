/*
 * The dashboard's trend charts, drawn as SVG: stacked bars (with an optional rate line), lines,
 * and dots with whiskers, over dashed grid lines, coloured by the chart tokens through classes.
 * A chart is drawn at the width of its box (one unit of the SVG is one pixel), so its labels keep
 * their size in a narrow card. Each bucket can be clicked to list what it counts; from the
 * keyboard, the chart takes the focus, the arrow keys choose a bucket (its values are announced),
 * and Enter lists it. The sparklines of the metric tiles are drawn here too.
 */

import type { ComponentChildren, RefObject } from "preact";
import { useLayoutEffect, useRef, useState } from "preact/hooks";
import { fx } from "../graph/geometry.ts";

const H = 176;
const PAD = { left: 46, right: 46, top: 14, bottom: 28 };
/** The width a chart is drawn at until its box is measured, and the least it is drawn at. */
const DEFAULT_W = 560;
const MIN_W = 240;

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
  /** The chart's name, with how to use it from the keyboard. */
  label: string;
}

/** The drawing area of a chart of `n` buckets, `w` pixels wide. */
interface Geometry {
  w: number;
  n: number;
  plotW: number;
  plotH: number;
}

const geometryOf = (width: number, n: number): Geometry => {
  const w = Math.max(MIN_W, Math.round(width));
  return { w, n, plotW: w - PAD.left - PAD.right, plotH: H - PAD.top - PAD.bottom };
};
const slotWidth = (g: Geometry): number => g.plotW / Math.max(1, g.n);
const centerOf = (g: Geometry, i: number): number => PAD.left + slotWidth(g) * (i + 0.5);
const yOf = (g: Geometry, value: number, max: number): number =>
  PAD.top + g.plotH - (max > 0 ? (value / max) * g.plotH : 0);

/** A round maximum for an axis. */
function niceMax(value: number): number {
  if (value <= 0) return 1;
  const magnitude = 10 ** Math.floor(Math.log10(value));
  const step = [1, 2, 2.5, 5, 10].find((s) => s * magnitude >= value) ?? 10;
  return step * magnitude;
}

/** The width of an element, kept current as it changes. */
function useWidth(): [RefObject<HTMLDivElement>, number] {
  const box = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(DEFAULT_W);
  useLayoutEffect(() => {
    const element = box.current;
    if (!element) return;
    if (element.clientWidth > 0) setWidth(element.clientWidth);
    if (typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver((entries) => {
      const measured = entries[0]?.contentRect.width ?? 0;
      if (measured > 0) setWidth(measured);
    });
    observer.observe(element);
    return () => observer.disconnect();
  }, []);
  return [box, width];
}

/** Which bucket the keyboard has chosen, and the chart's keys. */
function usePicker(frame: Frame) {
  const [active, setActive] = useState<number | null>(null);
  const n = frame.labels.length;
  const onPick = frame.onPick;
  const props = onPick
    ? {
        tabIndex: 0,
        onKeyDown: (event: KeyboardEvent): void => {
          if (n === 0) return;
          const at = active ?? -1;
          let next: number | null = null;
          if (event.key === "ArrowRight") next = Math.min(n - 1, at + 1);
          else if (event.key === "ArrowLeft") next = at < 0 ? n - 1 : Math.max(0, at - 1);
          else if (event.key === "Home") next = 0;
          else if (event.key === "End") next = n - 1;
          else if ((event.key === "Enter" || event.key === " ") && active !== null) {
            event.preventDefault();
            onPick(active);
            return;
          }
          if (next === null) return;
          event.preventDefault();
          setActive(next);
        },
        onBlur: () => setActive(null),
      }
    : {};
  return { active, props };
}

function Chart({
  frame,
  children,
}: {
  frame: Frame;
  children: (g: Geometry) => ComponentChildren;
}) {
  const { active, props } = usePicker(frame);
  const [box, width] = useWidth();
  const g = geometryOf(width, frame.labels.length);
  return (
    <div class="chart-frame" ref={box}>
      <svg
        class="chart"
        width={g.w}
        height={H}
        viewBox={`0 0 ${g.w} ${H}`}
        role="group"
        aria-label={frame.label}
        {...props}
      >
        <Grid g={g} />
        {active !== null && (
          <rect
            class="slot-active"
            x={fx(PAD.left + slotWidth(g) * active)}
            y={PAD.top}
            width={fx(slotWidth(g))}
            height={g.plotH}
            rx={4}
          />
        )}
        {children(g)}
        <XLabels g={g} labels={frame.labels} />
        <Slots g={g} frame={frame} />
      </svg>
      <p class="sr-only" aria-live="polite">
        {active !== null ? (frame.titles[active] ?? "") : ""}
      </p>
    </div>
  );
}

function Grid({ g }: { g: Geometry }) {
  return (
    <g class="grid" aria-hidden="true">
      {[0, 0.5, 1].map((share) => (
        <line
          key={share}
          x1={PAD.left}
          x2={g.w - PAD.right}
          y1={fx(PAD.top + g.plotH * (1 - share))}
          y2={fx(PAD.top + g.plotH * (1 - share))}
          class={share === 0 ? "base" : undefined}
        />
      ))}
    </g>
  );
}

/** The x labels: as many as fit (at most six), evenly apart. */
function XLabels({ g, labels }: { g: Geometry; labels: readonly string[] }) {
  const n = labels.length;
  const fits = Math.max(2, Math.min(6, Math.floor(g.plotW / 56)));
  const every = Math.max(1, Math.ceil(n / fits));
  return (
    <g class="axis" aria-hidden="true">
      {labels.map((label, i) =>
        i % every === 0 || i === n - 1 ? (
          <text key={i} x={fx(centerOf(g, i))} y={H - 8} text-anchor="middle">
            {label}
          </text>
        ) : null,
      )}
    </g>
  );
}

function YLabel({
  g,
  max,
  format,
  right,
}: {
  g: Geometry;
  max: number;
  format: (v: number) => string;
  right?: boolean;
}) {
  const x = right ? g.w - PAD.right + 7 : PAD.left - 7;
  const anchor = right ? "start" : "end";
  return (
    <g class="axis" aria-hidden="true">
      <text x={x} y={PAD.top + 4} text-anchor={anchor}>
        {format(max)}
      </text>
      <text x={x} y={PAD.top + g.plotH} text-anchor={anchor}>
        {format(0)}
      </text>
    </g>
  );
}

/** Transparent slots over the buckets, which a click picks. */
function Slots({ g, frame }: { g: Geometry; frame: Frame }) {
  const width = slotWidth(g);
  const { onPick, titles } = frame;
  return (
    <g class="slots">
      {frame.labels.map((_, i) => (
        <rect
          key={i}
          class={onPick ? "slot pickable" : "slot"}
          x={fx(PAD.left + width * i)}
          y={PAD.top}
          width={fx(width)}
          height={g.plotH}
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
          <span class={`swatch ${s.className}`} aria-hidden="true" />
          {s.label}
        </span>
      ))}
    </div>
  );
}

/** Stacked bars per bucket, with an optional line of a rate (0 to 1) on its own axis. */
export function StackedBars({
  stacks,
  series,
  rate,
  ...frame
}: Frame & {
  stacks: readonly (readonly number[])[];
  series: readonly SeriesStyle[];
  rate?: readonly (number | null)[];
}) {
  const max = niceMax(Math.max(0, ...stacks.map((values) => values.reduce((a, b) => a + b, 0))));
  return (
    <Chart frame={frame}>
      {(g) => {
        const bar = Math.min(22, slotWidth(g) * 0.62);
        const segments: string[] = [];
        if (rate) {
          let open = false;
          rate.forEach((value, i) => {
            if (value === null) {
              open = false;
              return;
            }
            segments.push(`${open ? "L" : "M"}${fx(centerOf(g, i))} ${fx(yOf(g, value, 1))}`);
            open = true;
          });
        }
        return (
          <>
            <YLabel g={g} max={max} format={(v) => String(v)} />
            {rate && <YLabel g={g} max={1} format={(v) => `${Math.round(v * 100)}%`} right />}
            {stacks.map((values, i) => {
              let top = PAD.top + g.plotH;
              return (
                <g key={i}>
                  {values.map((value, k) => {
                    if (value <= 0) return null;
                    const height = (value / max) * g.plotH;
                    top -= height;
                    return (
                      <rect
                        key={k}
                        class={`bar ${series[k]?.className ?? ""}`}
                        x={fx(centerOf(g, i) - bar / 2)}
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
                <circle
                  key={i}
                  class="rate-dot"
                  cx={fx(centerOf(g, i))}
                  cy={fx(yOf(g, value, 1))}
                  r={2.6}
                />
              ),
            )}
          </>
        );
      }}
    </Chart>
  );
}

/** A line per series. */
export function Lines({
  series,
  values,
  format,
  ...frame
}: Frame & {
  series: readonly SeriesStyle[];
  values: readonly (readonly (number | null)[])[];
  format: (v: number) => string;
}) {
  const max = niceMax(Math.max(0, ...values.flat().map((v) => v ?? 0)));
  return (
    <Chart frame={frame}>
      {(g) => (
        <>
          <YLabel g={g} max={max} format={format} />
          {series.map((s, k) => {
            let open = false;
            const d = (values[k] ?? [])
              .map((value, i) => {
                if (value === null) {
                  open = false;
                  return "";
                }
                const part = `${open ? "L" : "M"}${fx(centerOf(g, i))} ${fx(yOf(g, value, max))}`;
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
                      cx={fx(centerOf(g, i))}
                      cy={fx(yOf(g, value, max))}
                      r={2.6}
                    />
                  ),
                )}
              </g>
            );
          })}
        </>
      )}
    </Chart>
  );
}

/** A dot at each median, and a whisker from it to the p90. */
export function Whiskers({
  medians,
  p90s,
  format,
  ...frame
}: Frame & {
  medians: readonly (number | null)[];
  p90s: readonly (number | null)[];
  format: (v: number) => string;
}) {
  const max = niceMax(Math.max(0, ...p90s.map((v) => v ?? 0), ...medians.map((v) => v ?? 0)));
  return (
    <Chart frame={frame}>
      {(g) => (
        <>
          <YLabel g={g} max={max} format={format} />
          {medians.map((median, i) => {
            if (median === null) return null;
            const x = fx(centerOf(g, i));
            const p90 = p90s[i] ?? median;
            return (
              <g key={i}>
                <line
                  class="whisker"
                  x1={x}
                  y1={fx(yOf(g, median, max))}
                  x2={x}
                  y2={fx(yOf(g, p90, max))}
                />
                <line
                  class="whisker"
                  x1={fx(centerOf(g, i) - 4)}
                  y1={fx(yOf(g, p90, max))}
                  x2={fx(centerOf(g, i) + 4)}
                  y2={fx(yOf(g, p90, max))}
                />
                <circle class="median" cx={x} cy={fx(yOf(g, median, max))} r={3.6} />
              </g>
            );
          })}
        </>
      )}
    </Chart>
  );
}

/** Small bars of the buckets for a metric tile (a bucket without a value is a dot on the base). */
export function Sparkline({
  values,
  tone = "",
}: {
  values: readonly (number | null)[];
  tone?: string;
}) {
  const n = values.length;
  if (n === 0) return null;
  const width = 76;
  const height = 30;
  const gap = n > 16 ? 1 : 2;
  const bar = Math.max(1, Math.min(6, (width - gap * (n - 1)) / n));
  const start = width - (bar * n + gap * (n - 1));
  const max = Math.max(0, ...values.map((v) => v ?? 0));
  return (
    <svg
      class={`spark ${tone}`}
      viewBox={`0 0 ${width} ${height}`}
      width={width}
      height={height}
      aria-hidden="true"
      focusable="false"
    >
      {values.map((value, i) => {
        const h = value === null || max <= 0 ? 1.5 : Math.max(2, (value / max) * (height - 2));
        return (
          <rect
            key={i}
            class={value === null ? "none" : undefined}
            x={fx(start + i * (bar + gap))}
            y={fx(height - h)}
            width={fx(bar)}
            height={fx(h)}
            rx={1}
          />
        );
      })}
    </svg>
  );
}
