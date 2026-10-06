import { expect, test } from "bun:test";
import fs from "node:fs";
import path from "node:path";
import { resolveAgents } from "../../src/agents/index.ts";
import {
  buildDesignPrompt,
  modelWriteFromWorkspace,
  readDesignReferences,
  safeDesignSpec,
  validateDesignInputs,
} from "../../src/harness/designs.ts";
import { loadWorkspace } from "../../src/model/index.ts";
import { tmpWorkspace } from "../helpers/workspace.ts";

test("design references retain original binary and long files for CLI and desktop readers", () => {
  const ws = tmpWorkspace();
  try {
    const materials = [
      { name: "scan.pdf", bytes: Buffer.from("%PDF-1.7\nOriginal bytes\n%%EOF") },
      { name: "image.png", bytes: Buffer.from([137, 80, 78, 71, 13, 10, 26, 10, 0, 255]) },
      { name: "source.custom", bytes: Buffer.from([0, 1, 254, 255]) },
      { name: "long.txt", bytes: Buffer.from("a".repeat(90_000) + "FULL_CONTENT_END") },
    ];
    for (const material of materials)
      fs.writeFileSync(path.join(ws.root, material.name), material.bytes);
    const references = readDesignReferences(
      ws.root,
      materials.map((material) => material.name),
    );
    const loaded = loadWorkspace(ws.root, { parseYaml: Bun.YAML.parse });
    for (const delivery of ["cli", "desktop"] as const) {
      const prompt = buildDesignPrompt({
        delivery,
        language: "en",
        request: "Model the work in these materials.",
        process: null,
        model: modelWriteFromWorkspace(loaded, "revision"),
        modelMeaning: loaded.model,
        references,
        sources: [],
        messages: [],
        root: ws.root,
      });
      // The manifest is machine-readable, not decoded PDF bytes or a cut-off text body.
      const section = prompt.split("## User references\n")[1]!.split("\n## Required sources")[0]!;
      const manifest = JSON.parse(section.slice(section.indexOf("[\n"))) as {
        absolutePath: string;
        bytes: number;
        sha256: string;
      }[];
      expect(manifest).toHaveLength(4);
      for (const [index, reference] of manifest.entries()) {
        expect(fs.readFileSync(reference.absolutePath)).toEqual(materials[index]!.bytes);
        expect(reference.bytes).toBe(materials[index]!.bytes.length);
        expect(reference.sha256).toMatch(/^[a-f0-9]{64}$/);
      }
      expect(section).not.toContain("%PDF-");
      expect(section).not.toContain("FULL_CONTENT_END");
      expect(section).toContain("If a file cannot be read");
      expect(references.every((reference) => !reference.truncated)).toBe(true);
    }
    fs.writeFileSync(path.join(ws.root, "image.png"), "changed");
    expect(() => validateDesignInputs(ws.root, references, [])).toThrow("changed since");
    expect(() => readDesignReferences(ws.root, ["../outside.pdf"])).toThrow();
    expect(() => readDesignReferences(ws.root, ["missing.pdf"])).toThrow("missing");
    expect(() => readDesignReferences(ws.root, ["docs"])).toThrow("not a file");
  } finally {
    ws.dispose();
  }
});

test("design readers can inspect originals without granting project writes", () => {
  const specs = resolveAgents({});
  const claude = safeDesignSpec(
    specs.find((spec) => spec.format === "claude")!,
    {},
    "/project",
  )!;
  expect(claude.args[claude.args.indexOf("--tools") + 1]).toBe("Read");
  expect(claude.args[claude.args.indexOf("--permission-mode") + 1]).toBe("plan");
  expect(claude.args[claude.args.indexOf("--add-dir") + 1]).toBe("/project");
  expect(claude.args).not.toContain("Bash");
  const codex = safeDesignSpec(
    specs.find((spec) => spec.format === "codex")!,
    {},
    "/project",
  )!;
  expect(codex.args[codex.args.indexOf("--sandbox") + 1]).toBe("workspace-write");
  expect(codex.args).toContain("sandbox_workspace_write.exclude_tmpdir_env_var=true");
  expect(codex.args).toContain("sandbox_workspace_write.exclude_slash_tmp=true");
  expect(codex.args).not.toContain("--add-dir");
  expect(codex.args).toContain("--ignore-user-config");
});
