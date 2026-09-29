import type { ServerEvent } from "../../src/shared/types.ts";
import type { Daemon } from "./daemon.ts";

export interface Subscription {
  /** The events received so far, oldest first. */
  events: ServerEvent[];
  close(): Promise<void>;
}

/** Subscribes to the daemon's event stream (`GET /api/events`) as a client that is not a browser. */
export async function subscribe(daemon: Pick<Daemon, "url" | "info">): Promise<Subscription> {
  const response = await fetch(new URL(`/api/events?token=${daemon.info.token}`, daemon.url));
  if (!response.ok || !response.body) throw new Error(`/api/events answered ${response.status}`);
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  const events: ServerEvent[] = [];
  let buffer = "";
  const reading = (async () => {
    for (;;) {
      const { done, value } = await reader.read().catch(() => ({ done: true, value: undefined }));
      if (done) return;
      buffer += decoder.decode(value, { stream: true });
      for (let end = buffer.indexOf("\n\n"); end >= 0; end = buffer.indexOf("\n\n")) {
        const data = buffer
          .slice(0, end)
          .split("\n")
          .find((line) => line.startsWith("data: "));
        buffer = buffer.slice(end + 2);
        if (data) events.push(JSON.parse(data.slice(6)) as ServerEvent);
      }
    }
  })();
  return {
    events,
    async close() {
      await reader.cancel().catch(() => {});
      await reading;
    },
  };
}
