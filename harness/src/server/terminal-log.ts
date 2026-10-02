/* Read-only terminal view of normalized run events. Closing it never stops the agent. */
import fs from "node:fs";
import path from "node:path";
import { loadWorkspace } from "../model/index.ts";
import { parseYaml } from "./yaml.ts";
import { sayReceived } from "../shared/strings.ts";
import type { Run, RunEvent } from "../shared/types.ts";

/** Strip all terminal controls except line breaks and tabs, preserving Unicode. */
const safe = (text: string): string =>
  [...text]
    .filter((ch) => {
      const code = ch.codePointAt(0)!;
      return ch === "\n" || ch === "\t" || (code >= 32 && (code < 127 || code > 159));
    })
    .join("");
export async function showTerminalLog(root: string, id: string): Promise<void> {
  if (!/^r\d+$/.test(id)) throw new Error("Invalid run id.");
  const dir = path.join(root, ".alps-harness", "runs");
  const recordFile = path.join(dir, `${id}.json`);
  if (!fs.existsSync(recordFile)) throw new Error("This run is unavailable.");
  const language = loadWorkspace(root, { parseYaml }).language;
  console.log(
    language === "ja"
      ? `ALPS · ${id} · 実行ログ（閲覧のみ）\n閉じても実行は続きます。\n`
      : `ALPS · ${id} · Run log (read only)\nClosing this window leaves the run running.\n`,
  );
  let decoder = new TextDecoder();
  let offset = 0;
  let buffer = "";
  const file = path.join(dir, `${id}.jsonl`);
  for (;;) {
    if (fs.existsSync(file)) {
      const size = fs.statSync(file).size;
      if (size < offset) {
        offset = 0;
        buffer = "";
        decoder = new TextDecoder();
      }
      if (size > offset) {
        const fd = fs.openSync(file, "r");
        try {
          const chunk = Buffer.alloc(Math.min(size - offset, 1024 * 1024));
          const read = fs.readSync(fd, chunk, 0, chunk.length, offset);
          offset += read;
          buffer += decoder.decode(chunk.subarray(0, read), { stream: true });
          let end: number;
          while ((end = buffer.indexOf("\n")) >= 0) {
            const line = buffer.slice(0, end);
            buffer = buffer.slice(end + 1);
            try {
              const event = JSON.parse(line) as RunEvent;
              if (typeof event.text === "string")
                console.log(
                  `[${event.n}] ${new Date(event.t).toLocaleTimeString(language)} ${safe(sayReceived(language, event.key, event.args, event.text))}`,
                );
            } catch {
              /* An incomplete line stays in the writer's file; it is not a terminal command. */
            }
          }
        } finally {
          fs.closeSync(fd);
        }
        if (offset < size) continue;
      }
    }
    const run = JSON.parse(fs.readFileSync(recordFile, "utf8")) as Run;
    if (run.status !== "running") {
      console.log(`\n${safe(run.status)}${run.error ? ` · ${safe(run.error)}` : ""}`);
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
}
