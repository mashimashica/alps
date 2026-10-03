/* Metadata-only protocol replies shared by the fake run, wake, and assessment agents. */
import { createInterface } from "node:readline";

export async function fakeModels(args: string[]): Promise<boolean> {
  const codex = args.includes("app-server");
  if (!codex && !args.includes("--input-format")) return false;
  const model = process.env.ALPS_FAKE_MODEL ?? "future-model";
  for await (const line of createInterface({ input: process.stdin })) {
    const request = JSON.parse(line);
    if (codex && request.method === "initialize") {
      console.log(JSON.stringify({ id: request.id, result: {} }));
    } else if (codex && request.method === "model/list") {
      console.log(
        JSON.stringify({
          id: request.id,
          result: {
            data: [
              {
                model,
                displayName: "Future model",
                supportedReasoningEfforts: [
                  { reasoningEffort: "low" },
                  { reasoningEffort: "high" },
                ],
                defaultReasoningEffort: "low",
              },
            ],
            nextCursor: null,
          },
        }),
      );
      return true;
    } else if (!codex && request.request?.subtype === "initialize") {
      console.log(
        JSON.stringify({
          type: "control_response",
          response: {
            subtype: "success",
            request_id: request.request_id,
            response: {
              models: [
                {
                  value: model,
                  displayName: "Future model",
                  supportedEffortLevels: ["low", "high"],
                },
              ],
            },
          },
        }),
      );
      return true;
    }
  }
  return true;
}
