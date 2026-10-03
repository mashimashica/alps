/* Button, after shadcn/ui's: variants of emphasis and sizes, a busy state, and `type="button"` unless told. */

import type { ButtonHTMLAttributes } from "preact";
import { cx } from "./util.ts";

export type ButtonVariant = "default" | "secondary" | "outline" | "ghost" | "destructive" | "link";
export type ButtonSize = "default" | "sm" | "lg" | "icon" | "icon-sm";

export interface ButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "size"> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  /** Shows a spinner and marks the button busy; it stays in place so the layout does not jump. */
  busy?: boolean;
}

export function Button({
  variant = "default",
  size = "default",
  busy = false,
  class: extra,
  className,
  type = "button",
  children,
  ...rest
}: ButtonProps) {
  return (
    <button
      type={type}
      class={cx(
        "btn",
        `btn-${variant}`,
        `btn-${size}`,
        busy && "is-busy",
        extra as string,
        className as string,
      )}
      aria-busy={busy || undefined}
      {...rest}
    >
      {busy && <span class="spinner" aria-hidden="true" />}
      {children}
    </button>
  );
}
