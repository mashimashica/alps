/*
 * Native inputs dressed like shadcn/ui's: Checkbox and Switch are <input type="checkbox"> with
 * appearance: none (keyboard, form state, and focus stay the browser's), and Segmented is a
 * group of radio inputs shown as one row of choices (the arrow keys move within the group).
 */

import type { ComponentChildren } from "preact";
import { useId } from "preact/hooks";
import { cx } from "./util.ts";

export function Checkbox({
  checked,
  onChange,
  label,
  description,
  disabled = false,
  ariaLabel,
  class: extra,
}: {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: ComponentChildren;
  description?: ComponentChildren;
  disabled?: boolean;
  /** A name for assistive technology when the label alone does not say what the box does. */
  ariaLabel?: string;
  class?: string;
}) {
  const id = useId();
  return (
    <label class={cx("check-row", disabled && "is-disabled", extra)} for={id}>
      <input
        id={id}
        type="checkbox"
        class="checkbox"
        checked={checked}
        disabled={disabled}
        aria-label={ariaLabel}
        onChange={(event) => onChange(event.currentTarget.checked)}
      />
      <span class="check-text">
        <span class="check-label">{label}</span>
        {description && <span class="check-description">{description}</span>}
      </span>
    </label>
  );
}

export function Switch({
  checked,
  onChange,
  label,
  description,
  title,
  class: extra,
}: {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: ComponentChildren;
  description?: ComponentChildren;
  /** A tooltip, where the label is not shown. */
  title?: string;
  class?: string;
}) {
  const id = useId();
  return (
    <label class={cx("switch-row", extra)} for={id} title={title}>
      <span class="check-text">
        <span class="check-label">{label}</span>
        {description && <span class="check-description">{description}</span>}
      </span>
      <input
        id={id}
        type="checkbox"
        role="switch"
        class="switch"
        checked={checked}
        onChange={(event) => onChange(event.currentTarget.checked)}
      />
    </label>
  );
}

export interface SegmentOption<T extends string> {
  value: T;
  label: ComponentChildren;
  /** Colours the chosen option (achieved, not achieved, unverified). */
  tone?: string;
}

export function Segmented<T extends string>({
  name,
  value,
  options,
  onChange,
  labelledBy,
  invalid = false,
  class: extra,
}: {
  name: string;
  value: T;
  options: readonly SegmentOption<T>[];
  onChange: (value: T) => void;
  labelledBy?: string;
  invalid?: boolean;
  class?: string;
}) {
  return (
    <div
      class={cx("segmented", extra)}
      role="radiogroup"
      aria-labelledby={labelledBy}
      aria-invalid={invalid || undefined}
    >
      {options.map((option) => (
        <label
          key={option.value}
          class={cx("segment", option.tone && `tone-${option.tone}`)}
          data-checked={value === option.value ? "true" : undefined}
        >
          <input
            type="radio"
            class="segment-input"
            name={name}
            value={option.value}
            checked={value === option.value}
            onChange={() => onChange(option.value)}
          />
          <span>{option.label}</span>
        </label>
      ))}
    </div>
  );
}
