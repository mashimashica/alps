/*
 * The WebUI. For now it shows its heading and the result of /api/health.
 * UI strings move to a dictionary (strings.ts) when the English/Japanese switch arrives.
 */

import { render } from "preact";
import { useEffect, useState } from "preact/hooks";
import type { HealthInfo } from "../shared/types.ts";

type HealthState =
  | { status: "loading" }
  | { status: "ok"; health: HealthInfo }
  | { status: "error"; message: string };

/**
 * The per-start token arrives in the URL fragment (`#token=…`), which the browser never sends to
 * the server. It is read once and removed from the address bar and the history; the API gets it
 * in the X-Harness-Token header (the event stream, which cannot send headers, in `?token=`).
 */
function takeToken(): string | null {
  const fragment = new URLSearchParams(location.hash.slice(1));
  const token = fragment.get("token");
  if (token !== null) {
    fragment.delete("token");
    const rest = fragment.toString();
    history.replaceState(
      history.state,
      "",
      `${location.pathname}${location.search}${rest ? `#${rest}` : ""}`,
    );
  }
  return token;
}

const TOKEN = takeToken();

async function readJson<T>(response: Response): Promise<T> {
  if (!response.ok) throw new Error(`${response.url} answered ${response.status}`);
  return (await response.json()) as T;
}

async function fetchHealth(): Promise<HealthInfo> {
  if (!TOKEN)
    throw new Error("this page has no token. Open the URL that alps-harness serve printed.");
  return readJson<HealthInfo>(
    await fetch("/api/health", { headers: { "X-Harness-Token": TOKEN }, cache: "no-store" }),
  );
}

function App() {
  const [state, setState] = useState<HealthState>({ status: "loading" });
  useEffect(() => {
    fetchHealth().then(
      (health) => setState({ status: "ok", health }),
      (error: unknown) =>
        setState({
          status: "error",
          message: error instanceof Error ? error.message : String(error),
        }),
    );
  }, []);

  return (
    <main>
      <h1>ALPS Harness</h1>
      <p data-testid="health" data-status={state.status}>
        {state.status === "loading" && "Checking the server…"}
        {state.status === "ok" &&
          `Server ok: version ${state.health.version}, pid ${state.health.pid}, port ${state.health.port}, workspace ${state.health.workspace}`}
        {state.status === "error" && `Server unreachable: ${state.message}`}
      </p>
    </main>
  );
}

const root = document.getElementById("app");
if (root) render(<App />, root);
