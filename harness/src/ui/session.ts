/*
 * The per-start token and the screen to open. Both arrive in the URL fragment
 * (`#token=…&view=…`), which the browser never sends to the server. They are read once and removed
 * from the address bar and the history; the token is kept in sessionStorage so that the page
 * survives a reload (it goes when the tab closes). The API gets the token in the X-Harness-Token
 * header; the event stream, which cannot send headers, in `?token=`. The page's language, theme,
 * and transparency are the viewer's choices, kept in localStorage.
 */

import type { Language, UiView } from "../shared/types.ts";

const TOKEN_KEY = "alps-harness:token";
const VIEW_KEY = "alps-harness:view";
const LANGUAGE_KEY = "alps-harness:language";
const THEME_KEY = "alps-harness:theme";
const GLASS_KEY = "alps-harness:transparency";
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

/** The colour theme: the system's (prefers-color-scheme), or light or dark whatever it says. */
export type Theme = "system" | "light" | "dark";

export function keptTheme(): Theme {
  const value = local.read(THEME_KEY);
  return value === "light" || value === "dark" ? value : "system";
}

export const keepTheme = (theme: Theme): void => local.write(THEME_KEY, theme);

/** Whether surfaces are translucent: `null` until chosen (prefers-reduced-transparency decides). */
export function keptTransparency(): boolean | null {
  const value = local.read(GLASS_KEY);
  return value === "on" ? true : value === "off" ? false : null;
}

export const keepTransparency = (on: boolean): void => local.write(GLASS_KEY, on ? "on" : "off");

/**
 * Puts the theme and the transparency on the root element, where the tokens of tokens.css read
 * them: `data-theme` only when a theme is chosen (otherwise the system's applies through the
 * media query), and `data-glass` only when the transparency is chosen.
 */
export function applyDisplay(theme: Theme, transparency: boolean | null): void {
  const root = document.documentElement;
  if (theme === "system") delete root.dataset.theme;
  else root.dataset.theme = theme;
  if (transparency === null) delete root.dataset.glass;
  else root.dataset.glass = transparency ? "on" : "off";
}
