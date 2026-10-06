import fs from "node:fs";
import path from "node:path";
import type { ProjectFileEntry, ProjectFilesResponse } from "../shared/types.ts";
import { workspacePath } from "./paths.ts";
import { refuse } from "./errors.ts";

const PAGE_SIZE = 100;
const SEARCH_ENTRIES = 10_000;
const forbidden = (value: string): boolean =>
  value.split(/[\\/]/).some((part) => [".git", ".alps-harness"].includes(part.toLowerCase()));
const normalize = (value: string): string => value.normalize("NFKC").toLocaleLowerCase();

/** Metadata only, for a person's material picker; it does not read file contents or copy files. */
export async function projectFiles(
  root: string,
  options: { path: string; query: string; offset: number },
): Promise<ProjectFilesResponse> {
  const realRoot = fs.realpathSync(root);
  const inside = (target: string): boolean => {
    const relative = path.relative(realRoot, target);
    return (
      relative === "" ||
      (relative !== ".." && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative))
    );
  };
  const given = options.path || ".";
  const checked = given === "." ? { ok: true as const, path: "." } : workspacePath(root, given);
  if (!checked.ok || forbidden(given))
    throw refuse("outside-workspace", "error.outside", { where: "artifact", path: given, root });
  const current = checked.path.replace(/\/$/, "");
  let absolute: string;
  try {
    absolute = fs.realpathSync(path.resolve(root, current));
  } catch {
    throw refuse("not-found", "error.artifactRead", { path: given });
  }
  if (!inside(absolute) || forbidden(path.relative(realRoot, absolute)))
    throw refuse("outside-workspace", "error.outside", { where: "artifact", path: given, root });
  const term = normalize(options.query.trim());
  const entries: ProjectFileEntry[] = [];
  const pending = [current];
  const seen = new Set<string>();
  let scanned = 0;
  let incomplete = false;
  while (pending.length) {
    const directory = pending.shift()!;
    let children: fs.Dirent[];
    let real: string;
    try {
      real = await fs.promises.realpath(path.resolve(root, directory));
      if (!inside(real) || forbidden(path.relative(realRoot, real))) {
        if (directory === current) throw new Error("Directory is no longer available");
        incomplete = true;
        continue;
      }
      if (seen.has(real)) continue;
      seen.add(real);
      children = await fs.promises.readdir(real, { withFileTypes: true });
    } catch {
      if (directory === current)
        throw refuse("not-found", "error.artifactRead", { path: directory });
      incomplete = true;
      continue;
    }
    children.sort((a, b) => a.name.localeCompare(b.name));
    for (const child of children) {
      if (forbidden(child.name)) continue;
      if (term && scanned++ >= SEARCH_ENTRIES) {
        incomplete = true;
        break;
      }
      const relative = directory === "." ? child.name : `${directory}/${child.name}`;
      const matches = !term || normalize(relative).includes(term);
      let directoryEntry = child.isDirectory();
      if (!matches && !directoryEntry && !child.isSymbolicLink()) continue;
      if (!child.isFile() && !directoryEntry && !child.isSymbolicLink()) continue;
      let readable = true;
      // Dirents already describe ordinary files. Only links need target resolution during search;
      // checking access for every unmatched file makes large repositories needlessly slow.
      if (child.isSymbolicLink()) {
        try {
          const target = await fs.promises.realpath(path.join(real, child.name));
          if (!inside(target)) throw new Error("Outside the project");
          if (forbidden(path.relative(realRoot, target))) continue;
          const stat = await fs.promises.stat(target);
          if (!stat.isFile() && !stat.isDirectory()) continue;
          directoryEntry = stat.isDirectory();
        } catch {
          readable = false;
        }
      }
      if (matches)
        entries.push({ path: relative, name: child.name, directory: directoryEntry, readable });
      if (term && directoryEntry) {
        if (readable) pending.push(relative);
        else incomplete = true;
      }
    }
    if (!term || scanned > SEARCH_ENTRIES) break;
  }
  entries.sort((a, b) => Number(b.directory) - Number(a.directory) || a.path.localeCompare(b.path));
  const next = options.offset + PAGE_SIZE;
  const page = entries.slice(options.offset, next);
  await Promise.all(
    page.map(async (entry) => {
      if (!entry.readable) return;
      try {
        const target = await fs.promises.realpath(path.join(root, entry.path));
        if (!inside(target) || forbidden(path.relative(realRoot, target)))
          throw new Error("Unavailable");
        await fs.promises.access(
          target,
          fs.constants.R_OK | (entry.directory ? fs.constants.X_OK : 0),
        );
      } catch {
        entry.readable = false;
        if (term && entry.directory) incomplete = true;
      }
    }),
  );
  return {
    ok: true,
    path: current,
    entries: page,
    next: next < entries.length ? next : null,
    incomplete,
  };
}
