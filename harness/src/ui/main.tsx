/*
 * The WebUI's entry point. The token and the screen to open come in the URL fragment, which the
 * page reads once and removes from the address bar (session.ts).
 */

import { render } from "preact";
import { App } from "./app.tsx";
import { takeSession } from "./session.ts";

const session = takeSession();
const root = document.getElementById("app");
if (root) render(<App session={session} />, root);
