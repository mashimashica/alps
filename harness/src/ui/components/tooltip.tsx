/*
 * Tooltip: a short description of a control, shown in the top layer while the pointer rests on
 * it or the keyboard focus is on it, and hidden by Esc. The control names the tooltip with
 * aria-describedby, so assistive technology reads it whether or not it shows.
 */

import type { VNode } from "preact";
import { useEffect, useId, useLayoutEffect, useRef, useState } from "preact/hooks";
import { placeNear, setPopover } from "./util.ts";

export interface TooltipTrigger {
  "aria-describedby": string;
  onPointerEnter: (event: PointerEvent) => void;
  onPointerLeave: () => void;
  onFocus: (event: FocusEvent) => void;
  onBlur: () => void;
  onKeyDown: (event: KeyboardEvent) => void;
}

const DELAY_MS = 350;

export function Tooltip({
  content,
  children,
}: {
  content: string;
  children: (trigger: TooltipTrigger) => VNode;
}) {
  const id = useId();
  const tip = useRef<HTMLDivElement>(null);
  const anchor = useRef<HTMLElement | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const [open, setOpen] = useState(false);

  useLayoutEffect(() => {
    const element = tip.current;
    if (!element) return;
    setPopover(element, open);
    if (open && anchor.current) placeNear(element, anchor.current, { gap: 8 });
  }, [open]);
  useEffect(() => () => clearTimeout(timer.current), []);

  const hide = (): void => {
    clearTimeout(timer.current);
    setOpen(false);
  };
  const trigger: TooltipTrigger = {
    "aria-describedby": id,
    onPointerEnter: (event) => {
      anchor.current = event.currentTarget as HTMLElement;
      clearTimeout(timer.current);
      timer.current = setTimeout(() => setOpen(true), DELAY_MS);
    },
    onPointerLeave: hide,
    onFocus: (event) => {
      const target = event.currentTarget as HTMLElement;
      // Only the keyboard's focus shows it at once; a click already says what it wanted.
      if (!target.matches(":focus-visible")) return;
      anchor.current = target;
      setOpen(true);
    },
    onBlur: hide,
    onKeyDown: (event) => {
      if (event.key === "Escape" && open) hide();
    },
  };
  return (
    <>
      {children(trigger)}
      <div
        ref={tip}
        id={id}
        role="tooltip"
        popover="manual"
        class="tooltip"
        data-open={open ? "true" : undefined}
      >
        {content}
      </div>
    </>
  );
}
