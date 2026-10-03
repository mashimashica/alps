/* Card: a glass surface with an optional heading row (title, description, actions). */

import type { ComponentChildren } from "preact";
import { cx } from "./util.ts";

export function Card({
  class: extra,
  children,
  as: Tag = "section",
  ...data
}: {
  class?: string;
  children: ComponentChildren;
  as?: "section" | "div" | "article";
  [attribute: `data-${string}`]: string | undefined;
}) {
  return (
    <Tag class={cx("card", extra)} {...data}>
      {children}
    </Tag>
  );
}

export function CardHeader({
  title,
  description,
  actions,
  icon,
  level = 3,
}: {
  title: ComponentChildren;
  description?: ComponentChildren;
  actions?: ComponentChildren;
  icon?: ComponentChildren;
  level?: 2 | 3;
}) {
  const Heading = level === 2 ? "h2" : "h3";
  return (
    <div class="card-header">
      <div class="card-heading">
        <Heading class="card-title">
          {icon && <span class="card-icon">{icon}</span>}
          {title}
        </Heading>
        {description && <p class="card-description">{description}</p>}
      </div>
      {actions && <div class="card-actions">{actions}</div>}
    </div>
  );
}
