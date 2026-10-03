/*
 * Dialog and Sheet on the native <dialog>, opened with showModal() when they mount: the browser
 * keeps the focus inside, makes the rest of the page inert, and draws the backdrop. Esc (the
 * cancel event) and a press on the backdrop ask the page to close them (onClose), so the page's
 * state decides; when one goes, the focus returns to the element that had it when it opened.
 */

import type { ComponentChildren } from "preact";
import { useId, useLayoutEffect, useRef } from "preact/hooks";
import { Button } from "./button.tsx";
import { Icon } from "./icons.tsx";
import { cx } from "./util.ts";

/** Opens the dialog on mount, closes it on unmount, and gives the focus back. */
function useModal(onClose: () => void) {
  const ref = useRef<HTMLDialogElement>(null);
  const pressed = useRef(false);
  const close = useRef(onClose);
  close.current = onClose;
  useLayoutEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    const opener = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    if (!dialog.open) dialog.showModal();
    return () => {
      if (dialog.open) dialog.close();
      if (opener?.isConnected) opener.focus();
    };
  }, []);
  return {
    ref,
    onCancel: (event: Event): void => {
      event.preventDefault();
      close.current();
    },
    // Only a press that starts and ends on the backdrop closes it (not a text selection dragged out).
    onPointerDown: (event: PointerEvent): void => {
      pressed.current = event.target === ref.current;
    },
    onClick: (event: MouseEvent): void => {
      if (pressed.current && event.target === ref.current) close.current();
      pressed.current = false;
    },
  };
}

export function Dialog({
  title,
  description,
  onClose,
  closeLabel,
  size = "md",
  class: extra,
  testid,
  children,
}: {
  title: ComponentChildren;
  description?: ComponentChildren;
  onClose: () => void;
  closeLabel: string;
  size?: "md" | "lg";
  class?: string;
  testid?: string;
  children: ComponentChildren;
}) {
  const modal = useModal(onClose);
  const id = useId();
  return (
    <dialog
      ref={modal.ref}
      class={cx("dialog", `dialog-${size}`, extra)}
      aria-labelledby={`${id}-title`}
      aria-describedby={description ? `${id}-description` : undefined}
      data-testid={testid}
      onCancel={modal.onCancel}
      onPointerDown={modal.onPointerDown}
      onClick={modal.onClick}
    >
      <div class="dialog-surface">
        <div class="dialog-header">
          <h2 class="dialog-title" id={`${id}-title`}>
            {title}
          </h2>
          {description && (
            <p class="dialog-description" id={`${id}-description`}>
              {description}
            </p>
          )}
        </div>
        {children}
        <Button
          variant="ghost"
          size="icon-sm"
          class="dialog-close"
          aria-label={closeLabel}
          title={closeLabel}
          onClick={onClose}
        >
          <Icon name="x" />
        </Button>
      </div>
    </dialog>
  );
}

/** A panel that slides over the page from the right, for narrow windows. */
export function Sheet({
  label,
  onClose,
  class: extra,
  children,
}: {
  label: string;
  onClose: () => void;
  class?: string;
  children: ComponentChildren;
}) {
  const modal = useModal(onClose);
  return (
    <dialog
      ref={modal.ref}
      class={cx("sheet", extra)}
      aria-label={label}
      onCancel={modal.onCancel}
      onPointerDown={modal.onPointerDown}
      onClick={modal.onClick}
    >
      <div class="sheet-surface">{children}</div>
    </dialog>
  );
}
