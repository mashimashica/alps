/*
 * Text fields and the field around a control: a label bound to it, a hint, and an error that
 * sets the control's invalid state (aria-invalid) and is read with it (aria-describedby).
 */

import type { ComponentChildren, InputHTMLAttributes, TextareaHTMLAttributes, VNode } from "preact";
import { useId } from "preact/hooks";
import { Icon, type IconName } from "./icons.tsx";
import { cx } from "./util.ts";

export interface FieldControl {
  /** The control's id, which the label names. */
  id: string;
  /** The label's id, for controls that take aria-labelledby (Select). */
  labelId: string;
  describedBy: string | undefined;
  invalid: boolean;
}

export function Field({
  label,
  hint,
  error,
  warning,
  required = false,
  class: extra,
  children,
}: {
  label: ComponentChildren;
  hint?: ComponentChildren;
  /** Why the value cannot be saved; it marks the control invalid. */
  error?: ComponentChildren;
  /** What to know about a value that is saved anyway. */
  warning?: ComponentChildren;
  required?: boolean;
  class?: string;
  children: (control: FieldControl) => VNode;
}) {
  const id = useId();
  const hintId = `${id}-hint`;
  const noteId = `${id}-note`;
  const described = [hint ? hintId : "", error || warning ? noteId : ""].filter(Boolean).join(" ");
  return (
    <div class={cx("field", extra)} data-invalid={error ? "true" : undefined}>
      <label class="field-label" for={id} id={`${id}-label`}>
        {label}
        {required && (
          <span class="field-required" aria-hidden="true">
            *
          </span>
        )}
      </label>
      {children({
        id,
        labelId: `${id}-label`,
        describedBy: described || undefined,
        invalid: Boolean(error),
      })}
      {hint && (
        <p class="field-hint" id={hintId}>
          {hint}
        </p>
      )}
      {(error || warning) && (
        <p class={error ? "field-error" : "field-warning"} id={noteId}>
          <Icon name={error ? "alert" : "info"} size={14} />
          <span>{error ?? warning}</span>
        </p>
      )}
    </div>
  );
}

export function Input({
  invalid = false,
  icon,
  class: extra,
  ...rest
}: Omit<InputHTMLAttributes<HTMLInputElement>, "icon"> & { invalid?: boolean; icon?: IconName }) {
  const input = (
    <input
      class={cx("input", icon && "has-icon", extra as string)}
      aria-invalid={invalid || undefined}
      {...rest}
    />
  );
  if (!icon) return input;
  return (
    <span class="input-wrap">
      <Icon name={icon} class="input-icon" />
      {input}
    </span>
  );
}

export function Textarea({
  invalid = false,
  class: extra,
  ...rest
}: TextareaHTMLAttributes<HTMLTextAreaElement> & { invalid?: boolean }) {
  return (
    <textarea
      class={cx("input", "textarea", extra as string)}
      aria-invalid={invalid || undefined}
      {...rest}
    />
  );
}
