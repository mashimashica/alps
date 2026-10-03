/*
 * Select, after shadcn/ui's (a Radix select) but without dependencies: the select-only combobox
 * of the WAI-ARIA Authoring Practices. The trigger keeps the focus and names the active option
 * with aria-activedescendant; the options are a listbox shown in the top layer (the popover
 * attribute), so no card, table, or dialog clips it, and placed next to the trigger with
 * getBoundingClientRect through style properties. Keys: ↓ ↑ Home End PageDown PageUp move,
 * typed characters jump to the next option that starts with them, Enter and Space choose, Tab
 * chooses and moves on, Esc closes without a change (and does not close a dialog around it). A
 * press outside closes it.
 */

import type { ComponentChildren } from "preact";
import { useEffect, useId, useLayoutEffect, useRef, useState } from "preact/hooks";
import { Icon } from "./icons.tsx";
import { cx, placeNear, setPopover } from "./util.ts";

export interface SelectOption<T extends string> {
  value: T;
  label: string;
  /** A second line in the list. */
  hint?: string;
  disabled?: boolean;
  icon?: ComponentChildren;
}

export interface SelectProps<T extends string> {
  value: T;
  options: readonly SelectOption<T>[];
  onChange: (value: T) => void;
  /** The id of a visible label (a Field's labelId). */
  labelledBy?: string;
  /** The accessible name when no label is visible. */
  label?: string;
  id?: string;
  describedBy?: string;
  invalid?: boolean;
  disabled?: boolean;
  /** Shown while no option has the value. */
  placeholder?: string;
  /** Shown before the value (the chosen option's own icon wins). */
  icon?: ComponentChildren;
  size?: "default" | "sm";
  /** Only the icon shows in the trigger; the value stays there for assistive technology. */
  compact?: boolean;
  class?: string;
  testid?: string;
}

const PAGE = 8;
const TYPE_AHEAD_MS = 700;

export function Select<T extends string>(props: SelectProps<T>) {
  const { value, options, onChange } = props;
  const base = useId();
  const triggerId = props.id ?? `${base}-trigger`;
  const listId = `${base}-list`;
  const optionId = (i: number): string => `${base}-option-${i}`;
  const trigger = useRef<HTMLButtonElement>(null);
  const list = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(-1);
  const typed = useRef({ text: "", at: 0 });
  const chosen = options.findIndex((o) => o.value === value);
  const current = chosen >= 0 ? options[chosen] : undefined;

  const enabled = (i: number): boolean =>
    i >= 0 && i < options.length && options[i]?.disabled !== true;
  const step = (from: number, delta: number): number => {
    let found = from;
    for (
      let i = from + Math.sign(delta), moved = 0;
      i >= 0 && i < options.length;
      i += Math.sign(delta)
    ) {
      if (!enabled(i)) continue;
      found = i;
      if (++moved >= Math.abs(delta)) break;
    }
    return found;
  };
  const first = (): number => step(-1, 1);
  const last = (): number => step(options.length, -1);

  const show = (at: number): void => {
    setActive(enabled(at) ? at : first());
    setOpen(true);
  };
  const choose = (i: number): void => {
    const option = options[i];
    if (option && enabled(i) && option.value !== value) onChange(option.value);
    setOpen(false);
  };
  const place = (): void => {
    if (list.current && trigger.current)
      placeNear(list.current, trigger.current, { matchWidth: true, maxHeight: 320 });
  };

  useLayoutEffect(() => {
    const element = list.current;
    if (!element) return;
    setPopover(element, open);
    if (open) place();
  }, [open]);

  // Attached as the list opens (not after the next paint), so that no early press outside is missed.
  useLayoutEffect(() => {
    if (!open) return;
    const outside = (event: PointerEvent): void => {
      const target = event.target as Node | null;
      if (target && (trigger.current?.contains(target) || list.current?.contains(target))) return;
      setOpen(false);
    };
    const moved = (event: Event): void => {
      if (event.target instanceof Node && list.current?.contains(event.target)) return;
      place();
    };
    document.addEventListener("pointerdown", outside, true);
    window.addEventListener("resize", moved);
    window.addEventListener("scroll", moved, true);
    return () => {
      document.removeEventListener("pointerdown", outside, true);
      window.removeEventListener("resize", moved);
      window.removeEventListener("scroll", moved, true);
    };
  }, [open]);

  // Keep the active option in sight inside the list (without scrolling the page).
  useEffect(() => {
    const box = list.current;
    const option = open && active >= 0 ? document.getElementById(optionId(active)) : null;
    if (!box || !option) return;
    const top = option.offsetTop;
    const bottom = top + option.offsetHeight;
    if (top < box.scrollTop) box.scrollTop = top - 4;
    else if (bottom > box.scrollTop + box.clientHeight)
      box.scrollTop = bottom - box.clientHeight + 4;
  }, [open, active]);

  /** The next option whose label starts with what was typed; a repeated letter cycles. */
  const typeAhead = (key: string, from: number): number | null => {
    const now = Date.now();
    const text =
      now - typed.current.at < TYPE_AHEAD_MS
        ? typed.current.text + key.toLowerCase()
        : key.toLowerCase();
    typed.current = { text, at: now };
    const repeated = [...text].every((c) => c === text[0]);
    const needle = repeated ? (text[0] ?? "") : text;
    const start = repeated ? from + 1 : Math.max(from, 0);
    for (let k = 0; k < options.length; k++) {
      const i = (start + k + options.length) % options.length;
      if (enabled(i) && (options[i]?.label ?? "").toLowerCase().startsWith(needle)) return i;
    }
    return null;
  };

  const printable = (event: KeyboardEvent): boolean =>
    event.key.length === 1 && !event.ctrlKey && !event.metaKey && !event.altKey;

  const onKeyDown = (event: KeyboardEvent): void => {
    const key = event.key;
    if (!open) {
      if (key === "ArrowDown" || key === "ArrowUp" || key === "Enter" || key === " ") {
        event.preventDefault();
        show(chosen >= 0 ? chosen : first());
      } else if (key === "Home" || key === "End") {
        event.preventDefault();
        show(key === "Home" ? first() : last());
      } else if (printable(event)) {
        const found = typeAhead(key, chosen);
        if (found !== null) {
          event.preventDefault();
          show(found);
        }
      }
      return;
    }
    switch (key) {
      case "ArrowDown":
        event.preventDefault();
        setActive(step(active, 1));
        return;
      case "ArrowUp":
        event.preventDefault();
        if (event.altKey) choose(active);
        else setActive(step(active, -1));
        return;
      case "Home":
        event.preventDefault();
        setActive(first());
        return;
      case "End":
        event.preventDefault();
        setActive(last());
        return;
      case "PageDown":
        event.preventDefault();
        setActive(step(active, PAGE));
        return;
      case "PageUp":
        event.preventDefault();
        setActive(step(active, -PAGE));
        return;
      case "Enter":
      case " ":
        event.preventDefault();
        choose(active);
        return;
      case "Escape":
        // Closing the list is all that Esc does: a dialog around it stays open.
        event.preventDefault();
        event.stopPropagation();
        setOpen(false);
        return;
      case "Tab":
        choose(active);
        return;
      default:
        if (printable(event)) {
          const found = typeAhead(key, active);
          if (found !== null) {
            event.preventDefault();
            setActive(found);
          }
        }
    }
  };

  const icon = current?.icon ?? props.icon;
  return (
    <div
      class={cx(
        "select",
        props.size === "sm" && "select-sm",
        props.compact && "select-compact",
        props.class,
      )}
      data-testid={props.testid}
    >
      <button
        ref={trigger}
        type="button"
        id={triggerId}
        class="select-trigger"
        role="combobox"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={listId}
        aria-labelledby={props.labelledBy}
        aria-label={props.labelledBy ? undefined : props.label}
        aria-describedby={props.describedBy}
        aria-invalid={props.invalid || undefined}
        aria-activedescendant={open && active >= 0 ? optionId(active) : undefined}
        disabled={props.disabled}
        data-state={open ? "open" : "closed"}
        title={props.compact ? current?.label : undefined}
        onClick={() => (open ? setOpen(false) : show(chosen >= 0 ? chosen : first()))}
        onKeyDown={onKeyDown}
      >
        {icon && <span class="select-icon">{icon}</span>}
        <span class={cx("select-value", !current && "is-placeholder")}>
          {current?.label ?? props.placeholder ?? ""}
        </span>
        <Icon name="chevronDown" class="select-chevron" />
      </button>
      <div
        ref={list}
        id={listId}
        role="listbox"
        popover="manual"
        class="select-list"
        data-open={open ? "true" : undefined}
        aria-labelledby={props.labelledBy}
        aria-label={props.labelledBy ? undefined : props.label}
        tabIndex={-1}
      >
        {options.map((option, i) => (
          <div
            key={option.value}
            id={optionId(i)}
            role="option"
            aria-selected={i === chosen}
            aria-disabled={option.disabled || undefined}
            class={cx("select-option", i === active && "is-active")}
            // The trigger keeps the focus while the list is used with a pointer.
            onPointerDown={(event) => event.preventDefault()}
            onPointerMove={() => {
              if (enabled(i) && active !== i) setActive(i);
            }}
            onClick={() => {
              if (!enabled(i)) return;
              choose(i);
              trigger.current?.focus();
            }}
          >
            {option.icon && <span class="select-icon">{option.icon}</span>}
            <span class="select-option-text">
              <span>{option.label}</span>
              {option.hint && <span class="select-option-hint">{option.hint}</span>}
            </span>
            {i === chosen && <Icon name="check" class="select-check" />}
          </div>
        ))}
      </div>
    </div>
  );
}
