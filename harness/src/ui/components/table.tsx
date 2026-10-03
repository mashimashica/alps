/*
 * Table: a native table in a box that scrolls sideways when the columns do not fit. Rows that
 * open something are focusable and open it with Enter or Space as with a click (rowActions).
 */

import type { ComponentChildren } from "preact";
import { cx } from "./util.ts";

export function Table({
  children,
  class: extra,
  label,
}: {
  children: ComponentChildren;
  class?: string;
  /** The table's name for assistive technology, when no caption says it. */
  label?: string;
}) {
  return (
    <div class="table-wrap">
      <table class={cx("table", extra)} role="table" aria-label={label}>
        {children}
      </table>
    </div>
  );
}

/** The attributes of a row that opens something. */
export const rowActions = (open: () => void) => ({
  tabIndex: 0,
  class: "is-clickable",
  onClick: open,
  onKeyDown: (event: KeyboardEvent): void => {
    if (event.key !== "Enter" && event.key !== " ") return;
    if (event.target !== event.currentTarget) return;
    event.preventDefault();
    open();
  },
});
