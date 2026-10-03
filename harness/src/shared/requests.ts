/*
 * What a request to a wake may carry: how long its text may be, and the files that a person
 * attaches to it in the WebUI (POST /api/attachments), how many and how large, and where each is
 * saved. Files go to the workspace's attachments directory (`attachments` in alps-harness.yaml,
 * inbox/ by default), into a directory for the day in local time, under their own names made
 * harmless; a name already taken there gets -2, -3, … before its extension, up to -1000.
 * Constants and pure functions without imports, so that the WebUI checks the same limits; the
 * server checks the real directories (symlinks included) and writes the files.
 */

/**
 * The longest request text that a wake takes, in characters. The prompt reaches the agent on its
 * command line, so longer text belongs in an attached file.
 */
export const MAX_REQUEST_LENGTH = 20_000;

/** Where attachments go when alps-harness.yaml names no directory. */
export const DEFAULT_ATTACHMENTS = "inbox/";
/** The largest file that one attachment may be. */
export const MAX_ATTACHMENT_BYTES = 20 * 1024 * 1024;
/** The limit as the messages say it. */
export const MAX_ATTACHMENT_SIZE = "20 MB";
/** The most files that one request attaches, and one upload saves. */
export const MAX_ATTACHMENTS = 10;
/** The name given to a file whose own name leaves nothing once made harmless. */
export const FALLBACK_NAME = "attachment";
/** How many names an attachment tries in the day's directory: its own, then -2 to -1000. */
export const MAX_NAME_CANDIDATES = 1000;
/** Names are kept within this many bytes (UTF-8), below what file systems take, leaving room for -2. */
const MAX_NAME_BYTES = 200;

const bytes = (text: string): number => new TextEncoder().encode(text).length;

/** Whether a code point is a control character (C0, DEL, or C1). */
const isControl = (code: number): boolean => code <= 0x1f || (code >= 0x7f && code <= 0x9f);

/** A name cut to `limit` bytes of UTF-8 without splitting a character. */
function cut(text: string, limit: number): string {
  let kept = "";
  for (const char of text) {
    if (bytes(kept + char) > limit) break;
    kept += char;
  }
  return kept;
}

/**
 * A file name made harmless: only its last segment (after `/` or `\`), without control
 * characters and `..`, without leading dots and spaces, and within 200 bytes (the stem is cut
 * before the extension); `attachment` when nothing is left.
 */
export function safeFileName(given: string): string {
  let name = given.split(/[\\/]/).pop() ?? "";
  name = [...name].filter((char) => !isControl(char.codePointAt(0) ?? 0)).join("");
  while (name.includes("..")) name = name.replaceAll("..", "");
  name = name.replace(/^[.\s]+/, "").trim();
  if (bytes(name) > MAX_NAME_BYTES) {
    const dot = name.lastIndexOf(".");
    const extension = dot > 0 && bytes(name.slice(dot)) <= 20 ? name.slice(dot) : "";
    name = `${cut(name.slice(0, name.length - extension.length), MAX_NAME_BYTES - bytes(extension))}${extension}`;
  }
  return name || FALLBACK_NAME;
}

/**
 * `name`, or `name` with -2, -3, … up to -1000 before its extension, whichever `taken` first says
 * is free; `null` when all of them are taken.
 */
export function freeName(name: string, taken: (candidate: string) => boolean): string | null {
  if (!taken(name)) return name;
  const dot = name.lastIndexOf(".");
  const stem = dot > 0 ? name.slice(0, dot) : name;
  const extension = dot > 0 ? name.slice(dot) : "";
  for (let n = 2; n <= MAX_NAME_CANDIDATES; n++) {
    const candidate = `${stem}-${n}${extension}`;
    if (!taken(candidate)) return candidate;
  }
  return null;
}

/** The directory of a day, in local time: `YYYY-MM-DD`. */
export function dayOf(ms: number): string {
  const date = new Date(ms);
  const pad = (n: number): string => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

/**
 * Where an attachment is saved, relative to the workspace: `<dir><day>/<name>`, with the name
 * made harmless and free there; `null` when the name and its -2 to -1000 are all taken. `dir` is
 * the attachments directory with a trailing slash; `taken` says whether a path relative to the
 * workspace is in use.
 */
export function attachmentPath(
  dir: string,
  day: string,
  name: string,
  taken: (path: string) => boolean,
): string | null {
  const folder = `${dir}${day}/`;
  const free = freeName(safeFileName(name), (candidate) => taken(`${folder}${candidate}`));
  return free === null ? null : `${folder}${free}`;
}
