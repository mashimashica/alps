/*
 * Markdown in the WebUI (Plugin configuration, safety: "marked's output is made harmless"): HTML in
 * a SKILL.md, a report, or a note is shown as text; only http, https, and mailto links are links;
 * images are not loaded. The page's CSP (script-src 'self') is the second line of defence.
 */

import { describe, expect, test } from "bun:test";
import { linkUrl, renderMarkdown, splitFrontmatter } from "../../src/ui/markdown.ts";

describe("harmless Markdown", () => {
  test("HTML in the text is shown as text, in blocks and inline", () => {
    const html = renderMarkdown(
      '<script>alert(1)</script>\n\nA <img src=x onerror="alert(1)"> and <b>bold</b>.\n\n<iframe src="https://example.com"></iframe>',
    );
    expect(html).not.toMatch(/<(script|img|iframe|b)\b/i);
    expect(html).toContain("&lt;script&gt;alert(1)&lt;/script&gt;");
    expect(html).toContain("&lt;img src=x onerror=&quot;alert(1)&quot;&gt;");
    expect(html).toContain("&lt;b&gt;bold&lt;/b&gt;");
  });

  test("only http, https, and mailto links are links, opened without a referrer", () => {
    const html = renderMarkdown(
      "[a](https://example.com/x?y=1&z=2) [b](javascript:alert(1)) [c](JaVa\tScRiPt:alert(1)) [d](data:text/html,x) [e](vbscript:x) [f](mailto:a@example.com) [g](references/guide.md) <https://example.org>",
    );
    expect(html).toContain(
      '<a href="https://example.com/x?y=1&amp;z=2" title="https://example.com/x?y=1&amp;z=2" target="_blank" rel="noopener noreferrer">a</a>',
    );
    expect(html).toContain('href="mailto:a@example.com"');
    expect(html).toContain('href="https://example.org"');
    expect(html).not.toMatch(/href="(?:javascript|data|vbscript)/i);
    expect(html).not.toMatch(/href="[^"]*script/i);
    // A relative link names a file that the WebUI does not serve: it is kept as text.
    expect(html).toContain('<span class="md-link" title="references/guide.md">g</span>');
    expect([...html.matchAll(/<a /g)]).toHaveLength(3);
  });

  test("images are not loaded, and titles cannot break out of their attribute", () => {
    const html = renderMarkdown(
      '![a chart](https://tracker.example/pixel.png) [x](https://e.x "t\\" onmouseover=\\"alert(1)")',
    );
    expect(html).not.toContain("<img");
    expect(html).toContain(
      '<span class="md-image" title="https://tracker.example/pixel.png">a chart</span>',
    );
    expect(html).not.toMatch(/"\s+onmouseover=/);
  });

  test("the scheme of a link is read as a browser reads it", () => {
    expect(linkUrl("https://example.com")).toBe("https://example.com");
    expect(linkUrl(" java\nscript:alert(1)")).toBeNull();
    expect(linkUrl("#section")).toBeNull();
    expect(linkUrl("../other.md")).toBeNull();
  });

  test("a SKILL.md's frontmatter is shown apart from its body", () => {
    const { front, body } = splitFrontmatter(
      '---\nname: design-solution\ndescription: "Make a chosen solution concrete."\nmetadata:\n  version: 1\n---\n# Solution Design\n',
    );
    expect(front).toEqual([
      ["name", "design-solution"],
      ["description", "Make a chosen solution concrete."],
    ]);
    expect(body).toBe("# Solution Design\n");
    expect(splitFrontmatter("# No frontmatter").front).toEqual([]);
  });
});
