/*
 * The WebUI's entry point. The token and the screen to open come in the URL fragment, which the
 * page reads once and removes from the address bar (session.ts). The chosen theme and
 * transparency are put on the page before it is drawn, so it does not flash in the other theme.
 */

import { render } from "preact";
import { App } from "./app.tsx";
import { applyDisplay, keptTheme, keptTransparency, takeSession } from "./session.ts";

applyDisplay(keptTheme(), keptTransparency());
const session = takeSession();
const root = document.getElementById("app");
if (root) render(<App session={session} />, root);
