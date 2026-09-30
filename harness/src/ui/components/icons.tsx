/*
 * Line icons drawn for the WebUI on a 24-unit grid (stroked with the text colour). They are
 * decoration: each is hidden from assistive technology, and the control that holds one names
 * itself in words.
 */

import type { JSX } from "preact";

const PATHS = {
  chevronDown: <path d="m6 9 6 6 6-6" />,
  chevronRight: <path d="m9 6 6 6-6 6" />,
  check: <path d="M20 6 9 17l-5-5" />,
  x: <path d="M18 6 6 18M6 6l12 12" />,
  menu: <path d="M4 7h16M4 12h16M4 17h16" />,
  network: (
    <>
      <rect x="9" y="2.5" width="6" height="6" rx="1.3" />
      <rect x="2.5" y="15.5" width="6" height="6" rx="1.3" />
      <rect x="15.5" y="15.5" width="6" height="6" rx="1.3" />
      <path d="M12 8.5v4M5.5 15.5v-3h13v3" />
    </>
  ),
  dashboard: (
    <>
      <path d="M4 4v16h16" />
      <path d="M8.5 16v-4M12.5 16V8M16.5 16v-6" />
    </>
  ),
  layers: (
    <>
      <path d="m12 3.5 8.5 4.5-8.5 4.5L3.5 8z" />
      <path d="m3.5 12.5 8.5 4.5 8.5-4.5" />
      <path d="m3.5 16.5 8.5 4 8.5-4" />
    </>
  ),
  sun: (
    <>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2.5v2M12 19.5v2M4.6 4.6 6 6M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4" />
    </>
  ),
  moon: <path d="M20 14.2A8.2 8.2 0 0 1 9.8 4a8.2 8.2 0 1 0 10.2 10.2z" />,
  monitor: (
    <>
      <rect x="3" y="4" width="18" height="12.5" rx="2" />
      <path d="M8.5 20.5h7M12 16.5v4" />
    </>
  ),
  terminal: <path d="m5 6 5 5-5 5M13 17h6" />,
  plus: <path d="M12 5v14M5 12h14" />,
  play: <path d="M8 5.5v13l10-6.5z" />,
  stop: <rect x="6.5" y="6.5" width="11" height="11" rx="2" />,
  refresh: (
    <>
      <path d="M19.5 12a7.5 7.5 0 1 1-2.2-5.3" />
      <path d="M19.5 4.5v4.5H15" />
    </>
  ),
  info: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 11v5.5M12 7.8v.1" />
    </>
  ),
  alert: (
    <>
      <path d="M10.3 4.2 2.8 17.5A2 2 0 0 0 4.5 20.5h15a2 2 0 0 0 1.7-3L13.7 4.2a2 2 0 0 0-3.4 0z" />
      <path d="M12 9.5v4M12 16.8v.1" />
    </>
  ),
  clock: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 7.5V12l3 2" />
    </>
  ),
  search: (
    <>
      <circle cx="11" cy="11" r="6.5" />
      <path d="m20 20-4.2-4.2" />
    </>
  ),
  panel: (
    <>
      <rect x="3" y="4" width="18" height="16" rx="2.5" />
      <path d="M14.5 4v16" />
    </>
  ),
  file: (
    <>
      <path d="M14 3.5H7.5a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h9a2 2 0 0 0 2-2V8z" />
      <path d="M14 3.5V8h4.5" />
    </>
  ),
  target: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <circle cx="12" cy="12" r="4.5" />
      <circle cx="12" cy="12" r="1" />
    </>
  ),
  activity: <path d="M3 12h4l2.5-6.5 5 13L17 12h4" />,
  coins: (
    <>
      <ellipse cx="12" cy="6.5" rx="7" ry="3" />
      <path d="M5 6.5v5.5c0 1.7 3.1 3 7 3s7-1.3 7-3V6.5M5 12v5.5c0 1.7 3.1 3 7 3s7-1.3 7-3V12" />
    </>
  ),
  help: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M9.6 9.6a2.5 2.5 0 1 1 3.6 2.2c-.7.4-1.2 1-1.2 1.8v.4M12 16.9v.1" />
    </>
  ),
  history: (
    <>
      <path d="M3.5 12a8.5 8.5 0 1 0 2.6-6.1L3.5 8.5" />
      <path d="M3.5 4v4.5H8M12 8v4.2l3 1.8" />
    </>
  ),
  arrowUpRight: <path d="M7.5 16.5 16.5 7.5M9 7.5h7.5V15" />,
  arrowLeft: <path d="M19 12H5.5M11.5 18l-6-6 6-6" />,
  list: <path d="M9 6.5h11M9 12h11M9 17.5h11M4.5 6.5v.1M4.5 12v.1M4.5 17.5v.1" />,
  folder: (
    <path d="M3.5 7.5a2 2 0 0 1 2-2h3.8l2 2.2h7.2a2 2 0 0 1 2 2v7.8a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2z" />
  ),
  sliders: (
    <>
      <path d="M4 7h9M17 7h3M4 12h3M11 12h9M4 17h11M19 17h1" />
      <circle cx="15" cy="7" r="2" />
      <circle cx="9" cy="12" r="2" />
      <circle cx="17" cy="17" r="2" />
    </>
  ),
  languages: (
    <>
      <path d="M3.5 5.5h9M8 3.5v2M5.5 5.5c.9 3.1 3 5.6 6 7.3M10.5 5.5c-.9 3.1-3 5.6-6 7.3" />
      <path d="m13 20.5 4-9 4 9M14.4 17.5h5.2" />
    </>
  ),
} satisfies Record<string, JSX.Element>;

export type IconName = keyof typeof PATHS;

export function Icon({
  name,
  size = 16,
  class: extra,
}: {
  name: IconName;
  size?: number;
  class?: string;
}) {
  return (
    <svg
      class={extra ? `icon ${extra}` : "icon"}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="1.75"
      stroke-linecap="round"
      stroke-linejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      {PATHS[name]}
    </svg>
  );
}
