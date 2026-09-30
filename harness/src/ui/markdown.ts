/*
 * Markdown for the WebUI (a SKILL.md, a run's report, an evaluation's note), made harmless before
 * it reaches the page: HTML in the text is shown as text, only http, https, and mailto links are
 * links (they open in a new tab without a referrer), and images are not loaded. What remains is
 * the HTML that marked makes of the text itself. The page's CSP (script-src 'self') is the second
 * line: even HTML that got through could run no script.
 */

import { Marked } from "marked";

const ENTITIES: Record<string, string> = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;",
};

export const escapeHtml = (text: string): string =>
  text.replace(/[&<>"']/g, (c) => ENTITIES[c] ?? c);

/** The URL of a link that may be followed: http, https, or mailto; `null` for any other. */
export function linkUrl(href: string): string | null {
  // Browsers skip spaces and control characters in a scheme ("java\tscript:").
  const compact = [...href]
    .filter((char) => {
      const code = char.codePointAt(0) ?? 0;
      return code > 0x20 && (code < 0x7f || code > 0x9f);
    })
    .join("");
  const scheme = /^([a-z][a-z0-9+.-]*):/i.exec(compact)?.[1]?.toLowerCase();
  return scheme === "http" || scheme === "https" || scheme === "mailto" ? compact : null;
}

const markdown = new Marked({
  gfm: true,
  renderer: {
    html({ text }) {
      return escapeHtml(text);
    },
    link({ href, title, tokens }) {
      const inner = this.parser.parseInline(tokens);
      const url = linkUrl(href);
      const tip = escapeHtml(title ?? href);
      // A relative link names a file next to the document, which the WebUI does not serve.
      return url
        ? `<a href="${escapeHtml(url)}" title="${tip}" target="_blank" rel="noopener noreferrer">${inner}</a>`
        : `<span class="md-link" title="${tip}">${inner}</span>`;
    },
    image({ href, text }) {
      return `<span class="md-image" title="${escapeHtml(href)}">${escapeHtml(text)}</span>`;
    },
  },
});

/** Markdown as harmless HTML. */
export function renderMarkdown(source: string): string {
  return markdown.parse(source, { async: false });
}

/**
 * A SKILL.md's YAML frontmatter as its top-level `key: value` lines, and the body after it. Only
 * for showing: nested values are left out.
 */
export function splitFrontmatter(source: string): { front: [string, string][]; body: string } {
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/.exec(source);
  if (!match) return { front: [], body: source };
  const front: [string, string][] = [];
  for (const line of (match[1] ?? "").split(/\r?\n/)) {
    const pair = /^([A-Za-z0-9_-]+):\s*(.*)$/.exec(line);
    if (pair?.[1] && pair[2]) front.push([pair[1], pair[2].replace(/^(["'])(.*)\1$/, "$2")]);
  }
  return { front, body: source.slice(match[0].length) };
}
