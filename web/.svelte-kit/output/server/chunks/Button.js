import { T as attr, g as slot, s as attr_class, u as bind_props, vt as fallback, y as stringify } from "./index-server.js";
//#region src/lib/components/ui/Button.svelte
function Button($$renderer, $$props) {
	let variant = fallback($$props["variant"], "secondary");
	let type = fallback($$props["type"], "button");
	let disabled = fallback($$props["disabled"], false);
	$$renderer.push(`<button${attr("type", type)}${attr("disabled", disabled, true)}${attr_class(`button ${stringify(variant)}`)}><!--[-->`);
	slot($$renderer, $$props, "default", {}, null);
	$$renderer.push(`<!--]--></button>`);
	bind_props($$props, {
		variant,
		type,
		disabled
	});
}
//#endregion
export { Button as t };
