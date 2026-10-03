import fs from "node:fs";
import path from "node:path";
import type { Language } from "../shared/types.ts";
import { CONFIG_FILES, HARNESS_DIR, MODEL_FILES, ModelError, type ParseYaml } from "./files.ts";
import { loadWorkspace, type LoadedWorkspace } from "./load.ts";

export interface CreateWorkspaceOptions {
  root: string;
  name: string;
  language: Language;
  parseYaml: ParseYaml;
}

function yamlString(value: string): string {
  return JSON.stringify(value);
}

function existingSetup(root: string): string | null {
  for (const name of [...CONFIG_FILES, ...MODEL_FILES, HARNESS_DIR]) {
    if (fs.lstatSync(path.join(root, name), { throwIfNoEntry: false })) return name;
  }
  return null;
}

export function createWorkspace(options: CreateWorkspaceOptions): LoadedWorkspace {
  const root = path.resolve(options.root);
  const name = options.name.trim();
  if (!name) throw new ModelError("no-model", "Workspace name must not be empty.", [root]);
  if (!["en", "ja"].includes(options.language))
    throw new ModelError("no-model", `Unsupported workspace language: ${options.language}.`, [
      root,
    ]);

  const rootWasMissing = !fs.lstatSync(root, { throwIfNoEntry: false });
  const created: string[] = [];
  fs.mkdirSync(root, { recursive: true });
  try {
    const existing = existingSetup(root);
    if (existing)
      throw new ModelError(
        "no-model",
        `${root} is already an ALPS workspace (${existing} exists).`,
        [path.join(root, existing)],
      );

    const modelPath = path.join(root, "process-model.yaml");
    const configPath = path.join(root, "alps-harness.yaml");
    fs.writeFileSync(
      modelPath,
      ["draft: true", `name: ${yamlString(name)}`, "processes: []", "artifacts: []", ""].join("\n"),
      { flag: "wx" },
    );
    created.push(modelPath);
    fs.writeFileSync(
      configPath,
      [`model: ${yamlString("process-model.yaml")}`, `language: ${options.language}`, ""].join(
        "\n",
      ),
      { flag: "wx" },
    );
    created.push(configPath);
    return loadWorkspace(root, { parseYaml: options.parseYaml });
  } catch (error) {
    for (const file of created.reverse()) fs.rmSync(file, { force: true });
    if (rootWasMissing) {
      try {
        fs.rmdirSync(root);
      } catch {
        // Only remove an empty directory created for this initialization.
      }
    }
    throw error;
  }
}
