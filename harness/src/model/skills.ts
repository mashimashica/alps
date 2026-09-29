/* Finding the SKILL.md of each Process and its translations. */

import fs from "node:fs";
import path from "node:path";
import type { MissingSkill, Process, SkillLocation } from "../shared/types.ts";
import { SKIP_DIRS, isDir, isRecord, rel, type ParseYaml } from "./files.ts";

const MAX_DEPTH = 4;

/** Splits YAML frontmatter from a Markdown body. An unreadable frontmatter is dropped from the body only. */
export function splitFrontmatter(
  text: string,
  parseYaml: ParseYaml,
): { data: Record<string, unknown>; body: string } {
  const match = /^﻿?---\r?\n([\s\S]*?)\r?\n---[ \t]*(?:\r?\n|$)/.exec(text);
  if (!match) return { data: {}, body: text };
  let data: Record<string, unknown> = {};
  try {
    const parsed = parseYaml(match[1] ?? "");
    if (isRecord(parsed)) data = parsed;
  } catch {
    // Keep the body usable even when the frontmatter is not valid YAML.
  }
  return { data, body: text.slice(match[0].length) };
}

const firstHeading = (body: string): string =>
  /^#[ \t]+(.+?)[ \t#]*$/m.exec(body)?.[1]?.trim() ?? "";
const asText = (value: unknown): string =>
  typeof value === "string" ? value.trim() : typeof value === "number" ? String(value) : "";

/** Describes a SKILL.md and the translations in ALPS's layout (`references/locales/<lang>/SKILL.<lang>.md`). */
export function describeSkill(root: string, file: string, parseYaml: ParseYaml): SkillLocation {
  const { data, body } = splitFrontmatter(fs.readFileSync(file, "utf8"), parseYaml);
  const dir = path.dirname(file);
  const titles = [firstHeading(body)];
  const translations: SkillLocation["translations"] = [];
  const locales = path.join(dir, "references", "locales");
  if (isDir(locales)) {
    for (const lang of fs.readdirSync(locales).sort()) {
      const langDir = path.join(locales, lang);
      if (!isDir(langDir)) continue;
      for (const name of fs.readdirSync(langDir).sort()) {
        if (!/^SKILL\.[\w-]+\.md$/i.test(name)) continue;
        const translated = path.join(langDir, name);
        translations.push({ lang, path: rel(root, translated) });
        try {
          titles.push(
            firstHeading(splitFrontmatter(fs.readFileSync(translated, "utf8"), parseYaml).body),
          );
        } catch {
          // An unreadable translation does not make the Skill unusable.
        }
      }
    }
  }
  return {
    path: rel(root, file),
    dir: rel(root, dir),
    name: asText(data.name) || path.basename(dir),
    description: asText(data.description),
    titles: titles.filter(Boolean),
    translations,
  };
}

/** Every SKILL.md under the Skill roots of the workspace. */
export function findSkills(
  root: string,
  skillRoots: string[],
  parseYaml: ParseYaml,
): SkillLocation[] {
  const found: SkillLocation[] = [];
  const walk = (dir: string, depth: number): void => {
    let entries: fs.Dirent[];
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (SKIP_DIRS.has(entry.name)) continue;
      const p = path.join(dir, entry.name);
      if (entry.isFile() && entry.name === "SKILL.md") {
        try {
          found.push(describeSkill(root, p, parseYaml));
        } catch {
          // An unreadable SKILL.md is not a candidate.
        }
      } else if (entry.isDirectory() && depth < MAX_DEPTH && entry.name !== "references") {
        walk(p, depth + 1);
      }
    }
  };
  for (const skillRoot of skillRoots) {
    const base = path.join(root, skillRoot);
    if (isDir(base)) walk(base, 0);
  }
  return found;
}

/**
 * The Skill of a Process. A declared location wins; otherwise the frontmatter name,
 * the directory name, or a heading (of the Skill or a translation) must match the Process.
 */
export function skillFor(
  root: string,
  index: SkillLocation[],
  process: Process,
  parseYaml: ParseYaml,
): SkillLocation | MissingSkill | null {
  if (process.skill) {
    let file = path.resolve(root, process.skill);
    if (isDir(file)) file = path.join(file, "SKILL.md");
    try {
      return describeSkill(root, file, parseYaml);
    } catch {
      return { missing: process.skill };
    }
  }
  return (
    index.find(
      (skill) =>
        skill.name === process.id ||
        skill.name === process.name ||
        path.posix.basename(skill.dir) === process.id ||
        skill.titles.includes(process.name),
    ) ?? null
  );
}
