/*
 * Location patterns of Artifact types. Only `*` (within one path segment) and `**` (any number of
 * segments) are wildcards; every other character, `?` included, stands for itself. A trailing `/`
 * makes each matching directory one Artifact.
 */

export interface LocationPattern {
  /** The pattern as written, with forward slashes and without a leading `./`. */
  pattern: string;
  /** Matches directories only (the pattern ends with `/`). */
  dirOnly: boolean;
  regex: RegExp;
  /** The directory to scan from: the segments before the first wildcard (`""` for the workspace root). */
  prefix: string;
  /** How many segments below `prefix` a match lies, when the pattern has no `**`. */
  depth: number;
  /** Whether the pattern has `**`. */
  deep: boolean;
}

const hasWildcard = (segment: string): boolean => segment.includes("*");

/** `<case>` (and `{case}` from the YAML block form) of harness 0.8 is read as `*`. */
export const normalizeLocations = (patterns: string[]): string[] =>
  patterns.map((pattern) => pattern.replace(/<case>|\{case\}/g, "*"));

/** Whether a location names one file or directory rather than a pattern. */
export const isConcrete = (location: string): boolean => !location.includes("*");

export function compilePattern(pattern: string): LocationPattern {
  const normalized = pattern.replace(/\\/g, "/").replace(/^(?:\.\/)+/, "");
  const dirOnly = normalized.endsWith("/");
  const body = dirOnly ? normalized.replace(/\/+$/, "") : normalized;
  const segments = body.split("/");
  const fixed: string[] = [];
  for (const segment of segments) {
    if (hasWildcard(segment)) break;
    fixed.push(segment);
  }
  // A pattern without wildcards is scanned from its parent directory.
  if (fixed.length === segments.length) fixed.pop();

  let source = "";
  for (let i = 0; i < body.length; i++) {
    if (body.startsWith("**/", i)) {
      source += "(?:.*/)?";
      i += 2;
    } else if (body.startsWith("**", i)) {
      source += ".*";
      i += 1;
    } else if (body[i] === "*") {
      source += "[^/]*";
    } else {
      source += (body[i] ?? "").replace(/[.+?^$(){}|[\]\\]/g, "\\$&");
    }
  }
  return {
    pattern: normalized,
    dirOnly,
    regex: new RegExp(`^${source}$`),
    prefix: fixed.join("/"),
    depth: segments.length - fixed.length,
    deep: body.includes("**"),
  };
}

/** Whether a workspace-relative path (forward slashes, no trailing slash) is an Artifact of the pattern. */
export const matchesPattern = (
  compiled: LocationPattern,
  relPath: string,
  isDirectory: boolean,
): boolean => compiled.regex.test(relPath) && (!compiled.dirOnly || isDirectory);
