/* The model as the workspace realizes it, for get_model and the WebUI. */

import type { ModelDescription } from "../shared/types.ts";
import { rel, type ParseYaml } from "./files.ts";
import type { LoadedWorkspace } from "./load.ts";
import { findSkills, skillFor } from "./skills.ts";

export function describeModel(workspace: LoadedWorkspace, parseYaml: ParseYaml): ModelDescription {
  const { root, model } = workspace;
  const index = findSkills(root, workspace.skillRoots, parseYaml);
  return {
    workspace: root,
    modelPath: rel(root, workspace.modelPath),
    configPath: workspace.configPath ? rel(root, workspace.configPath) : null,
    language: workspace.language,
    name: model.name,
    description: model.description,
    processes: model.processes.map((process) => ({
      ...process,
      skill: skillFor(root, index, process, parseYaml),
    })),
    artifacts: model.artifacts,
  };
}
