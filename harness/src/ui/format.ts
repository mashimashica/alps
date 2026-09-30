/* Numbers, durations, money, and times as the WebUI shows them, in the page's language. */

import type { Language, Ratio } from "../shared/types.ts";

export const percent = (value: number | null): string =>
  value === null ? "—" : `${Math.round(value * 100)}`;

export const ratioText = (share: Ratio): string => percent(share.value);

/** A duration in the largest units that keep it readable. */
export function duration(ms: number | null, language: Language): string {
  if (ms === null) return "—";
  const ja = language === "ja";
  if (ms < 10_000) return `${(ms / 1000).toFixed(1)}${ja ? " 秒" : " s"}`;
  const seconds = Math.round(ms / 1000);
  if (seconds < 60) return `${seconds}${ja ? " 秒" : " s"}`;
  if (seconds < 3600)
    return ja
      ? `${Math.floor(seconds / 60)} 分 ${seconds % 60} 秒`
      : `${Math.floor(seconds / 60)} min ${seconds % 60} s`;
  const minutes = Math.floor((seconds % 3600) / 60);
  return ja
    ? `${Math.floor(seconds / 3600)} 時間 ${minutes} 分`
    : `${Math.floor(seconds / 3600)} h ${minutes} min`;
}

export const money = (usd: number | null): string =>
  usd === null ? "—" : usd < 0.01 && usd > 0 ? `$${usd.toFixed(4)}` : `$${usd.toFixed(2)}`;

export const count = (n: number | null, language: Language): string =>
  n === null ? "—" : n.toLocaleString(language === "ja" ? "ja-JP" : "en-US");

const locale = (language: Language): string => (language === "ja" ? "ja-JP" : "en-US");

export const dateTime = (ms: number, language: Language): string =>
  new Intl.DateTimeFormat(locale(language), { dateStyle: "medium", timeStyle: "short" }).format(
    new Date(ms),
  );

export const shortDate = (ms: number, language: Language): string =>
  new Intl.DateTimeFormat(locale(language), { month: "numeric", day: "numeric" }).format(
    new Date(ms),
  );

export const clock = (ms: number, language: Language): string =>
  new Intl.DateTimeFormat(locale(language), {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date(ms));
