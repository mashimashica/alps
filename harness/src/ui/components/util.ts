/* What the components share: class names put together, and a media query that the page follows. */

import { useEffect, useState } from "preact/hooks";

/** The class names that are set, separated by spaces. */
export const cx = (...names: (string | false | null | undefined)[]): string =>
  names.filter(Boolean).join(" ");

/** Whether a media query matches, kept current while the page is open. */
export function useMedia(query: string): boolean {
  const [matches, setMatches] = useState(() => window.matchMedia(query).matches);
  useEffect(() => {
    const list = window.matchMedia(query);
    const change = (): void => setMatches(list.matches);
    change();
    list.addEventListener("change", change);
    return () => list.removeEventListener("change", change);
  }, [query]);
  return matches;
}

/** Whether the browser puts `popover` elements in the top layer; without it, CSS shows them instead. */
export const popoverSupported = (): boolean =>
  typeof HTMLElement !== "undefined" && "showPopover" in HTMLElement.prototype;

/** Shows or hides a `popover` element; a no-op where the attribute is not supported. */
export function setPopover(element: HTMLElement, open: boolean): void {
  if (!popoverSupported()) return;
  const shown = element.matches(":popover-open");
  if (open && !shown) element.showPopover();
  else if (!open && shown) element.hidePopover();
}

/**
 * Places a floating element (in the top layer, so fixed to the viewport) next to its anchor:
 * below it, or above when there is more room there, kept inside the viewport. Sizes and
 * positions are set through the element's style properties, which the page's CSP allows.
 */
export function placeNear(
  floating: HTMLElement,
  anchor: HTMLElement,
  options: { gap?: number; matchWidth?: boolean; maxHeight?: number; prefer?: "top" | "bottom" },
): void {
  const gap = options.gap ?? 6;
  const margin = 8;
  const rect = anchor.getBoundingClientRect();
  const viewWidth = document.documentElement.clientWidth;
  const viewHeight = window.innerHeight;
  const style = floating.style;
  if (options.matchWidth) style.minWidth = `${Math.round(rect.width)}px`;
  style.maxWidth = `${viewWidth - margin * 2}px`;
  const below = viewHeight - rect.bottom - gap - margin;
  const above = rect.top - gap - margin;
  const natural = floating.scrollHeight;
  const cap = options.maxHeight ?? Number.POSITIVE_INFINITY;
  const up =
    options.prefer === "top"
      ? above >= Math.min(natural, cap) || above > below
      : below < Math.min(natural, cap, 220) && above > below;
  if (options.maxHeight !== undefined)
    style.maxHeight = `${Math.max(96, Math.min(cap, up ? above : below))}px`;
  const width = floating.offsetWidth;
  const left = Math.max(margin, Math.min(rect.left, viewWidth - width - margin));
  style.left = `${Math.round(left)}px`;
  if (up) {
    style.top = "auto";
    style.bottom = `${Math.round(viewHeight - rect.top + gap)}px`;
  } else {
    style.bottom = "auto";
    style.top = `${Math.round(rect.bottom + gap)}px`;
  }
}
