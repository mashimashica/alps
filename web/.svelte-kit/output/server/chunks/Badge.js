import { g as slot, s as attr_class, u as bind_props, vt as fallback, y as stringify } from "./index-server.js";
//#region src/lib/api.ts
var mutationMethods = /* @__PURE__ */ new Set([
	"POST",
	"PUT",
	"PATCH",
	"DELETE"
]);
var APIError = class extends Error {
	status;
	code;
	details;
	constructor(status, code, message, details) {
		super(message);
		this.status = status;
		this.code = code;
		this.details = details;
	}
};
async function api(path, init = {}) {
	const method = (init.method || "GET").toUpperCase();
	const headers = new Headers(init.headers);
	if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
	if (mutationMethods.has(method) && !headers.has("Idempotency-Key")) headers.set("Idempotency-Key", crypto.randomUUID());
	const response = await fetch(`/v1${path}`, {
		...init,
		headers
	});
	if (!response.ok) {
		const payload = await response.json().catch(() => ({ error: {
			code: "http_error",
			message: response.statusText
		} }));
		throw new APIError(response.status, payload.error?.code ?? "http_error", payload.error?.message ?? response.statusText, payload.error?.details);
	}
	if (response.status === 204) return void 0;
	return response.json();
}
function json(method, value) {
	return {
		method,
		body: JSON.stringify(value)
	};
}
//#endregion
//#region src/lib/components/ui/Badge.svelte
function Badge($$renderer, $$props) {
	let tone = fallback($$props["tone"], "neutral");
	$$renderer.push(`<span${attr_class(`badge ${stringify(tone)}`)}><!--[-->`);
	slot($$renderer, $$props, "default", {}, null);
	$$renderer.push(`<!--]--></span>`);
	bind_props($$props, { tone });
}
//#endregion
export { api as n, json as r, Badge as t };
