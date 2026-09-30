/* Badge: a short label with a tone (and an optional dot), for statuses and kinds. */

import type { ComponentChildren } from "preact";
import { cx } from "./util.ts";

export type Tone = "neutral" | "info" | "success" | "danger" | "warning" | "brand" | "outline";

export function Badge({
  tone = "neutral",
  dot = false,
  pulse = false,
  class: extra,
  title,
  children,
  ...data
}: {
  tone?: Tone;
  dot?: boolean;
  /** The dot breathes (a running run); still where motion is reduced. */
  pulse?: boolean;
  class?: string;
  title?: string;
  children: ComponentChildren;
  [attribute: `data-${string}`]: string | undefined;
}) {
  return (
    <span class={cx("badge", `badge-${tone}`, extra)} title={title} {...data}>
      {dot && <span class={cx("badge-dot", pulse && "pulse")} aria-hidden="true" />}
      {children}
    </span>
  );
}
