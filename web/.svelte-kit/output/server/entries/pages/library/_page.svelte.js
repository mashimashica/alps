import { A as writable, E as escape_html, O as derived, T as attr, b as unsubscribe_stores, c as attr_style, f as ensure_array_like, p as head, s as attr_class, u as bind_props, v as store_get, vt as fallback } from "../../../chunks/index-server.js";
import "../../../chunks/exports.js";
import { c as useQueryClient, t as createQuery } from "../../../chunks/createQuery.js";
import { a as createMutation, i as Portal, n as Dialog, r as Dialog_overlay, t as Dialog_content } from "../../../chunks/dialog-content.js";
import { t as goto } from "../../../chunks/client.js";
import "../../../chunks/navigation.js";
import { n as api, r as json, t as Badge } from "../../../chunks/Badge.js";
import { t as Button } from "../../../chunks/Button.js";
import { Virtualizer, elementScroll, observeElementOffset, observeElementRect } from "@tanstack/virtual-core";
//#region node_modules/@tanstack/svelte-virtual/dist/index.js
function createVirtualizerBase(initialOptions) {
	const virtualizer = new Virtualizer(initialOptions);
	const originalSetOptions = virtualizer.setOptions;
	let virtualizerWritable;
	const setOptions = (options) => {
		const resolvedOptions = {
			...virtualizer.options,
			...options,
			onChange: options.onChange
		};
		originalSetOptions({
			...resolvedOptions,
			onChange: (instance, sync) => {
				virtualizerWritable.set(instance);
				resolvedOptions.onChange?.(instance, sync);
			}
		});
		virtualizer._willUpdate();
		virtualizerWritable.set(virtualizer);
	};
	virtualizerWritable = writable(virtualizer, () => {
		setOptions(initialOptions);
		return virtualizer._didMount();
	});
	return derived(virtualizerWritable, (instance) => Object.assign(instance, { setOptions }));
}
function createVirtualizer(options) {
	return createVirtualizerBase({
		observeElementRect,
		observeElementOffset,
		scrollToFn: elementScroll,
		...options
	});
}
//#endregion
//#region src/lib/components/VirtualAssetList.svelte
function VirtualAssetList($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		var $$store_subs;
		let virtualizer;
		let items = fallback($$props["items"], () => [], true);
		let onSelect = $$props["onSelect"];
		let scroller;
		$: virtualizer = createVirtualizer({
			count: items.length,
			getScrollElement: () => scroller,
			estimateSize: () => 66,
			overscan: 8
		});
		$$renderer.push(`<div class="asset-scroll"><div class="virtual-space"${attr_style("", { height: `${store_get($$store_subs ??= {}, "$virtualizer", virtualizer).getTotalSize()}px` })}><!--[-->`);
		const each_array = ensure_array_like(store_get($$store_subs ??= {}, "$virtualizer", virtualizer).getVirtualItems());
		for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
			let row = each_array[$$index];
			const asset = items[row.index];
			$$renderer.push(`<button class="asset-row virtual-row"${attr_style("", { transform: `translateY(${row.start}px)` })}><span class="asset-icon">${escape_html(asset.kind === "skill" ? "S" : asset.kind === "plugin" ? "P" : "M")}</span> <span class="asset-copy"><strong>${escape_html(asset.name)}</strong><small>${escape_html(asset.kind)} · ${escape_html(asset.scope)}</small></span> <span class="asset-status">${escape_html(asset.alpsState === "changed" ? "Changed" : asset.alpsState === "adopted" ? "Adopted" : "›")}</span></button>`);
		}
		$$renderer.push(`<!--]--></div></div>`);
		if ($$store_subs) unsubscribe_stores($$store_subs);
		bind_props($$props, {
			items,
			onSelect
		});
	});
}
//#endregion
//#region src/lib/components/SafeMarkdown.svelte
function SafeMarkdown($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let blocks;
		let source = fallback($$props["source"], "");
		function parse(value) {
			const blocks = [];
			let code = false;
			let codeLines = [];
			for (const line of value.replace(/^---[\s\S]*?---\s*/m, "").split("\n")) {
				if (line.startsWith("```")) {
					if (code) {
						blocks.push({
							type: "code",
							text: codeLines.join("\n")
						});
						codeLines = [];
					}
					code = !code;
					continue;
				}
				if (code) {
					codeLines.push(line);
					continue;
				}
				if (line.startsWith("### ")) blocks.push({
					type: "h3",
					text: line.slice(4)
				});
				else if (line.startsWith("## ")) blocks.push({
					type: "h2",
					text: line.slice(3)
				});
				else if (line.startsWith("# ")) blocks.push({
					type: "h1",
					text: line.slice(2)
				});
				else if (/^[-*] /.test(line)) blocks.push({
					type: "li",
					text: line.slice(2)
				});
				else if (line.trim()) blocks.push({
					type: "p",
					text: line.trim()
				});
			}
			return blocks;
		}
		$: blocks = parse(source);
		$$renderer.push(`<div class="markdown"><!--[-->`);
		const each_array = ensure_array_like(blocks);
		for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
			let block = each_array[$$index];
			if (block.type === "h1") {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<h1>${escape_html(block.text)}</h1>`);
			} else if (block.type === "h2") {
				$$renderer.push("<!--[1-->");
				$$renderer.push(`<h2>${escape_html(block.text)}</h2>`);
			} else if (block.type === "h3") {
				$$renderer.push("<!--[2-->");
				$$renderer.push(`<h3>${escape_html(block.text)}</h3>`);
			} else if (block.type === "li") {
				$$renderer.push("<!--[3-->");
				$$renderer.push(`<div class="markdown-list"><span>•</span><p>${escape_html(block.text)}</p></div>`);
			} else if (block.type === "code") {
				$$renderer.push("<!--[4-->");
				$$renderer.push(`<pre><code>${escape_html(block.text)}</code></pre>`);
			} else {
				$$renderer.push("<!--[-1-->");
				$$renderer.push(`<p>${escape_html(block.text)}</p>`);
			}
			$$renderer.push(`<!--]-->`);
		}
		$$renderer.push(`<!--]--></div>`);
		bind_props($$props, { source });
	});
}
//#endregion
//#region src/lib/components/SkillViewer.svelte
function SkillViewer($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let action;
		let open = fallback($$props["open"], false);
		let assetId = fallback($$props["assetId"], "");
		const client = useQueryClient();
		let selectedPath = "";
		const detail = createQuery(() => ({
			queryKey: ["asset", assetId],
			queryFn: () => api(`/assets/${assetId}`),
			enabled: Boolean(open && assetId)
		}));
		const file = createQuery(() => ({
			queryKey: [
				"asset-content",
				assetId,
				selectedPath
			],
			queryFn: () => api(`/assets/${assetId}/content?path=${encodeURIComponent(selectedPath)}`),
			enabled: Boolean(open && assetId && selectedPath)
		}));
		const adopt = createMutation(() => ({
			mutationFn: () => api(`/assets/${assetId}/adopt`, json("POST", {})),
			onSuccess: async () => {
				await client.invalidateQueries({ queryKey: ["catalog"] });
				await client.invalidateQueries({ queryKey: ["asset", assetId] });
			}
		}));
		const start = createMutation(() => ({
			mutationFn: () => api("/runs", json("POST", {
				title: detail.data?.name,
				process: detail.data?.name,
				assetId
			})),
			onSuccess: async () => {
				open = false;
				await client.invalidateQueries({ queryKey: ["runs"] });
				await goto("/runs");
			}
		}));
		function close() {
			open = false;
			selectedPath = "";
		}
		$: if (detail.data && !selectedPath) selectedPath = detail.data.contentPath || detail.data.files?.[0] || "";
		$: action = detail.data?.alpsState === "adopted" ? "Start Run" : detail.data?.alpsState === "changed" ? "Compare Changes" : detail.data?.validation === "valid" ? "Adopt Skill" : "Review Validation";
		let $$settled = true;
		let $$inner_renderer;
		function $$render_inner($$renderer) {
			Dialog($$renderer, {
				onOpenChange: (value) => !value && close(),
				get open() {
					return open;
				},
				set open($$value) {
					open = $$value;
					$$settled = false;
				},
				children: ($$renderer) => {
					Portal($$renderer, {
						children: ($$renderer) => {
							Dialog_overlay($$renderer, { class: "dialog-overlay" });
							$$renderer.push(`<!----> `);
							Dialog_content($$renderer, {
								class: "dialog-content skill-viewer",
								"aria-label": "Skill package viewer",
								children: ($$renderer) => {
									if (detail.isPending) {
										$$renderer.push("<!--[0-->");
										$$renderer.push(`<div class="empty-state">Loading Skill…</div>`);
									} else if (detail.isError) {
										$$renderer.push("<!--[1-->");
										$$renderer.push(`<div class="empty-state error">${escape_html(detail.error.message)}</div>`);
									} else if (detail.data) {
										$$renderer.push("<!--[2-->");
										$$renderer.push(`<header class="viewer-header"><div class="viewer-identity"><span class="asset-icon">${escape_html(detail.data.kind === "skill" ? "S" : detail.data.kind === "plugin" ? "P" : "M")}</span><div><h2>${escape_html(detail.data.name)}</h2><p>${escape_html(detail.data.kind)} · ${escape_html(detail.data.scope)}</p></div></div> <button class="icon-close" aria-label="Close">×</button></header> <div class="viewer-grid"><nav class="package-tree" aria-label="Package files"><!--[-->`);
										const each_array = ensure_array_like(detail.data.files ?? []);
										for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
											let path = each_array[$$index];
											$$renderer.push(`<button${attr_class("", void 0, { "active": path === selectedPath })}>${escape_html(path)}</button>`);
										}
										$$renderer.push(`<!--]--></nav> <article class="viewer-document"><div class="document-summary">`);
										Badge($$renderer, {
											tone: detail.data.validation === "valid" ? "success" : "warning",
											children: ($$renderer) => {
												$$renderer.push(`<!---->${escape_html(detail.data.validation)}`);
											},
											$$slots: { default: true }
										});
										$$renderer.push(`<!----><p>${escape_html(detail.data.description || "No discovery description.")}</p></div> `);
										if (selectedPath.toLowerCase().endsWith(".md")) {
											$$renderer.push("<!--[0-->");
											SafeMarkdown($$renderer, { source: file.data?.content ?? detail.data.content ?? "" });
										} else {
											$$renderer.push("<!--[-1-->");
											$$renderer.push(`<pre class="raw-preview">${escape_html(file.data?.content ?? detail.data.content ?? "")}</pre>`);
										}
										$$renderer.push(`<!--]--></article></div> <footer class="viewer-footer">`);
										Button($$renderer, {
											variant: "primary",
											disabled: adopt.isPending || start.isPending,
											children: ($$renderer) => {
												$$renderer.push(`<!---->${escape_html(action)}`);
											},
											$$slots: { default: true }
										});
										$$renderer.push(`<!----></footer>`);
									} else $$renderer.push("<!--[-1-->");
									$$renderer.push(`<!--]-->`);
								},
								$$slots: { default: true }
							});
							$$renderer.push(`<!---->`);
						},
						$$slots: { default: true }
					});
				},
				$$slots: { default: true }
			});
		}
		do {
			$$settled = true;
			$$inner_renderer = $$renderer.copy();
			$$render_inner($$inner_renderer);
		} while (!$$settled);
		$$renderer.subsume($$inner_renderer);
		bind_props($$props, {
			open,
			assetId
		});
	});
}
//#endregion
//#region src/routes/library/+page.svelte
function _page($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let items;
		let search = "";
		let filter = "all";
		let viewerOpen = false;
		let assetId = "";
		const catalog = createQuery(() => ({
			queryKey: ["catalog"],
			queryFn: () => api("/catalog")
		}));
		function inspect(asset) {
			assetId = asset.id;
			viewerOpen = true;
		}
		$: items = (catalog.data ?? []).filter((asset) => true);
		let $$settled = true;
		let $$inner_renderer;
		function $$render_inner($$renderer) {
			head("c8k2rg", $$renderer, ($$renderer) => {
				$$renderer.title(($$renderer) => {
					$$renderer.push(`<title>Library · ALPS Local Runtime</title>`);
				});
			});
			$$renderer.push(`<section class="panel glass library-panel"><div class="library-toolbar"><input${attr("value", search)} class="search-input" placeholder="Search Skills, Plugins, and Models" aria-label="Search assets"/> <div class="segmented" role="tablist"><!--[-->`);
			const each_array = ensure_array_like([
				["all", "All"],
				["skill", "Skills"],
				["plugin", "Plugins"],
				["process-model", "Models"]
			]);
			for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
				let item = each_array[$$index];
				$$renderer.push(`<button${attr_class("", void 0, { "active": filter === item[0] })}>${escape_html(item[1])}</button>`);
			}
			$$renderer.push(`<!--]--></div></div> `);
			if (catalog.isPending) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<div class="empty-state">Discovering assets…</div>`);
			} else if (catalog.isError) {
				$$renderer.push("<!--[1-->");
				$$renderer.push(`<div class="empty-state error">${escape_html(catalog.error.message)}</div>`);
			} else {
				$$renderer.push("<!--[-1-->");
				VirtualAssetList($$renderer, {
					items,
					onSelect: inspect
				});
			}
			$$renderer.push(`<!--]--></section> `);
			SkillViewer($$renderer, {
				assetId,
				get open() {
					return viewerOpen;
				},
				set open($$value) {
					viewerOpen = $$value;
					$$settled = false;
				}
			});
			$$renderer.push(`<!---->`);
		}
		do {
			$$settled = true;
			$$inner_renderer = $$renderer.copy();
			$$render_inner($$inner_renderer);
		} while (!$$settled);
		$$renderer.subsume($$inner_renderer);
	});
}
//#endregion
export { _page as default };
