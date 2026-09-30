/*
 * Tabs with a roving tabindex (WAI-ARIA Authoring Practices): only the chosen tab is in the Tab
 * order; the arrow keys along the list (← → or ↑ ↓ when vertical), Home, and End move to another
 * tab and choose it. The page draws the chosen tab's panel with tabPanel().
 */

import type { ComponentChildren } from "preact";
import { useRef } from "preact/hooks";
import { cx } from "./util.ts";

export interface TabItem<T extends string> {
  value: T;
  label: ComponentChildren;
  icon?: ComponentChildren;
  /** A count after the label (part of the tab's name). */
  count?: number;
  /** A tooltip, for tabs whose label is not shown (the sidebar as a rail). */
  title?: string;
  /** Extra attributes of the tab (data-*). */
  attrs?: Record<`data-${string}`, string>;
}

const tabId = (base: string, value: string): string => `${base}-tab-${value}`;
const panelId = (base: string): string => `${base}-panel`;

export function Tabs<T extends string>({
  value,
  onChange,
  items,
  label,
  base,
  orientation = "horizontal",
  variant = "line",
  class: extra,
}: {
  value: T;
  onChange: (value: T) => void;
  items: readonly TabItem<T>[];
  label: string;
  /** Makes the ids of the tabs and of their panel. */
  base: string;
  orientation?: "horizontal" | "vertical";
  variant?: "line" | "pill" | "nav";
  class?: string;
}) {
  const tabs = useRef<(HTMLButtonElement | null)[]>([]);
  const move = (index: number): void => {
    const item = items[index];
    if (!item) return;
    tabs.current[index]?.focus();
    if (item.value !== value) onChange(item.value);
  };
  const onKeyDown = (event: KeyboardEvent, index: number): void => {
    const next = orientation === "vertical" ? "ArrowDown" : "ArrowRight";
    const previous = orientation === "vertical" ? "ArrowUp" : "ArrowLeft";
    const n = items.length;
    let target: number | null = null;
    if (event.key === next) target = (index + 1) % n;
    else if (event.key === previous) target = (index - 1 + n) % n;
    else if (event.key === "Home") target = 0;
    else if (event.key === "End") target = n - 1;
    if (target === null) return;
    event.preventDefault();
    move(target);
  };
  return (
    <div
      role="tablist"
      aria-label={label}
      aria-orientation={orientation}
      class={cx("tabs", `tabs-${variant}`, extra)}
    >
      {items.map((item, index) => {
        const selected = item.value === value;
        return (
          <button
            key={item.value}
            ref={(element) => {
              tabs.current[index] = element;
            }}
            type="button"
            role="tab"
            id={tabId(base, item.value)}
            aria-selected={selected}
            aria-controls={panelId(base)}
            tabIndex={selected ? 0 : -1}
            title={item.title}
            class="tab"
            onClick={() => onChange(item.value)}
            onKeyDown={(event) => onKeyDown(event, index)}
            {...item.attrs}
          >
            {item.icon}
            <span class="tab-label">{item.label}</span>
            {item.count !== undefined && <span class="tab-count">{item.count}</span>}
          </button>
        );
      })}
    </div>
  );
}

/** The attributes of the panel that the chosen tab controls. */
export const tabPanel = (base: string, value: string) => ({
  role: "tabpanel" as const,
  id: panelId(base),
  "aria-labelledby": tabId(base, value),
  tabIndex: 0,
});
