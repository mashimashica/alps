/*
 * What the page says about its own state: an inline notice (Alert), placeholders while something
 * loads (Skeleton), and the empty state of a list or a view (Empty).
 */

import type { ComponentChildren } from "preact";
import { Icon, type IconName } from "./icons.tsx";
import { cx } from "./util.ts";

export type AlertTone = "info" | "success" | "warning" | "danger";

const ALERT_ICONS: Record<AlertTone, IconName> = {
  info: "info",
  success: "check",
  warning: "history",
  danger: "alert",
};

/**
 * An inline notice. Failures are announced at once (`role="alert"`), the others politely
 * (`role="status"`); `live={false}` leaves a notice that was already there out of both.
 */
export function Alert({
  tone = "info",
  title,
  children,
  action,
  live = true,
  icon,
  class: extra,
  ...data
}: {
  tone?: AlertTone;
  title?: ComponentChildren;
  children?: ComponentChildren;
  action?: ComponentChildren;
  live?: boolean;
  icon?: IconName;
  class?: string;
  [attribute: `data-${string}`]: string | undefined;
}) {
  const role = !live ? undefined : tone === "danger" ? "alert" : "status";
  return (
    <div class={cx("alert", `alert-${tone}`, extra)} role={role} {...data}>
      <Icon name={icon ?? ALERT_ICONS[tone]} class="alert-icon" />
      <div class="alert-body">
        {title && <p class="alert-title">{title}</p>}
        {children}
      </div>
      {action && <div class="alert-action">{action}</div>}
    </div>
  );
}

/** A shimmering placeholder of a given size (through style properties, which the CSP allows). */
export function Skeleton({
  width,
  height,
  class: extra,
}: {
  width?: string;
  height?: string;
  class?: string;
}) {
  return (
    <span
      class={cx("skeleton", extra)}
      aria-hidden="true"
      style={{ ...(width ? { width } : {}), ...(height ? { height } : {}) }}
    />
  );
}

/** Lines of placeholders, announced once as loading. */
export function Loading({ label, lines = 3 }: { label: string; lines?: number }) {
  return (
    <div class="loading" role="status">
      <span class="sr-only">{label}</span>
      {Array.from({ length: lines }, (_, i) => (
        <Skeleton key={i} width={`${92 - ((i * 17) % 40)}%`} />
      ))}
    </div>
  );
}

export function Empty({
  icon = "list",
  title,
  description,
  action,
  class: extra,
}: {
  icon?: IconName;
  title: ComponentChildren;
  description?: ComponentChildren;
  action?: ComponentChildren;
  class?: string;
}) {
  return (
    <div class={cx("empty", extra)}>
      <span class="empty-icon" aria-hidden="true">
        <Icon name={icon} size={20} />
      </span>
      <p class="empty-title">{title}</p>
      {description && <p class="empty-description">{description}</p>}
      {action && <div class="empty-action">{action}</div>}
    </div>
  );
}
