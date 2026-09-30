/*
 * The per-start token and the screen to open. Both arrive in the URL fragment
 * (`#token=…&view=…`), which the browser never sends to the server. They are read once and removed
 * from the address bar and the history; the token is kept in sessionStorage so that the page
 * survives a reload (it goes when the tab closes). The API gets the token in the X-Harness-Token
 * header; the event stream, which cannot send headers, in `?token=`.
 */

import type { Language, UiView } from "../shared/types.ts";

const TOKEN_KEY = "alps-harness:token";
const VIEW_KEY = "alps-harness:view";
const LANGUAGE_KEY = "alps-harness:language";
const VIEWS: readonly UiView[] = ["network", "dashboard", "instances"];

/** Storage that may be missing (a private window, blocked site data): reads and writes never throw. */
function store(kind: "session" | "local") {
  const get = (): Storage | null => {
    try {
      return kind === "session" ? window.sessionStorage : window.localStorage;
    } catch {
      return null;
    }
  };
  return {
    read(key: string): string | null {
      try {
        return get()?.getItem(key) ?? null;
      } catch {
        return null;
      }
    },
    write(key: string, value: string): void {
      try {
        get()?.setItem(key, value);
      } catch {
        // Not kept: the page still works until it is reloaded.
      }
    },
  };
}

const session = store("session");
const local = store("local");

const isView = (value: string | null): value is UiView =>
  value !== null && (VIEWS as readonly string[]).includes(value);

export interface Session {
  token: string | null;
  view: UiView;
}

/** Takes the token and the view from the fragment, removes them from the URL, and keeps them. */
export function takeSession(): Session {
  const fragment = new URLSearchParams(location.hash.slice(1));
  const token = fragment.get("token");
  const view = fragment.get("view");
  if (token !== null || view !== null) {
    fragment.delete("token");
    fragment.delete("view");
    const rest = fragment.toString();
    history.replaceState(
      history.state,
      "",
      `${location.pathname}${location.search}${rest ? `#${rest}` : ""}`,
    );
  }
  if (token) session.write(TOKEN_KEY, token);
  if (isView(view)) session.write(VIEW_KEY, view);
  const kept = session.read(VIEW_KEY);
  return {
    token: token || session.read(TOKEN_KEY),
    view: isView(view) ? view : isView(kept) ? kept : "network",
  };
}

export const keepView = (view: UiView): void => session.write(VIEW_KEY, view);

export function keptLanguage(): Language | null {
  const value = local.read(LANGUAGE_KEY);
  return value === "en" || value === "ja" ? value : null;
}

export const keepLanguage = (language: Language): void => local.write(LANGUAGE_KEY, language);
