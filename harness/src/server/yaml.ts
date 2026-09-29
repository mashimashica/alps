import type { ParseYaml } from "../model/index.ts";

/** YAML through Bun's parser. Bun-specific APIs stay in src/server/ and src/cli.ts. */
export const parseYaml: ParseYaml = (text) => Bun.YAML.parse(text);
