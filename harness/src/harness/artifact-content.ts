import fs from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";
import type { ArtifactContent } from "../shared/types.ts";
import { workspacePath } from "./paths.ts";
import { refuse } from "./errors.ts";

const MAX_BYTES = 256 * 1024;
const MAX_ENTRIES = 200;
const forbidden = (value: string): boolean =>
  value.split(/[\\/]/).some((part) => part === ".git" || part === ".alps-harness");

export function artifactContent(root: string, given: string): ArtifactContent {
  const checked = workspacePath(root, given);
  if (!checked.ok || forbidden(given))
    throw refuse("outside-workspace", "error.outside", { where: "artifact", path: given, root });
  let real: string;
  try {
    real = fs.realpathSync(path.resolve(root, checked.path));
  } catch {
    throw refuse("not-found", "error.artifactRead", { path: given });
  }
  if (forbidden(path.relative(fs.realpathSync(root), real)))
    throw refuse("outside-workspace", "error.outside", { where: "artifact", path: given, root });
  const stat = fs.statSync(real);
  const common = {
    path: checked.path.replace(/\/$/, ""),
    observedAt: Date.now(),
    size: stat.size,
    modifiedAt: stat.mtimeMs,
    sha256: null,
  };
  if (stat.isDirectory()) {
    const entries = fs
      .readdirSync(real, { withFileTypes: true })
      .filter((item) => !forbidden(item.name))
      .sort(
        (a, b) => Number(b.isDirectory()) - Number(a.isDirectory()) || a.name.localeCompare(b.name),
      );
    return {
      ...common,
      kind: "directory",
      truncated: entries.length > MAX_ENTRIES,
      entries: entries.slice(0, MAX_ENTRIES).map((item) => {
        const relative = `${common.path}/${item.name}`;
        return {
          name: item.name,
          path: relative,
          directory: item.isDirectory(),
          readable: workspacePath(root, relative).ok,
        };
      }),
    };
  }
  if (!stat.isFile()) throw refuse("invalid-request", "error.artifactRead", { path: given });
  let fd: number | undefined;
  try {
    fd = fs.openSync(
      real,
      fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW | fs.constants.O_NONBLOCK,
    );
    if (!fs.fstatSync(fd).isFile()) throw new Error("Not a regular file");
    const bytes = Buffer.alloc(MAX_BYTES + 1);
    const count = fs.readSync(fd, bytes, 0, bytes.length, 0);
    const preview = bytes.subarray(0, Math.min(count, MAX_BYTES));
    const truncated = count > MAX_BYTES || stat.size > MAX_BYTES;
    const sha256 = truncated ? null : createHash("sha256").update(preview).digest("hex");
    if (preview.includes(0)) return { ...common, kind: "binary", sha256, truncated };
    // Never execute or embed workspace HTML; the client renders this as plain text.
    return { ...common, kind: "text", text: preview.toString("utf8"), sha256, truncated };
  } catch {
    throw refuse("invalid-request", "error.artifactRead", { path: given });
  } finally {
    if (fd !== undefined) fs.closeSync(fd);
  }
}
