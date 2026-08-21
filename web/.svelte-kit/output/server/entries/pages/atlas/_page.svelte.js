import { E as escape_html, T as attr, f as ensure_array_like, p as head, s as attr_class, u as bind_props, vt as fallback, y as stringify } from "../../../chunks/index-server.js";
import { t as createQuery } from "../../../chunks/createQuery.js";
import { n as api, t as Badge } from "../../../chunks/Badge.js";
import "d3-selection";
import { zoom, zoomIdentity } from "d3-zoom";
//#region src/lib/components/AtlasCanvas.svelte
function AtlasCanvas($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let processes, interfaces, positioned, byId, connected, selectedNode;
		let graph = $$props["graph"];
		let mode = fallback($$props["mode"], "structure");
		let onMode = $$props["onMode"];
		let selected = "";
		let transform = zoomIdentity;
		const center = {
			x: 500,
			y: 330
		};
		function radial(items, radius) {
			return items.map((node, index) => {
				const angle = -Math.PI / 2 + index * Math.PI * 2 / Math.max(1, items.length);
				return {
					...node,
					x: center.x + Math.cos(angle) * radius,
					y: center.y + Math.sin(angle) * radius
				};
			});
		}
		function muted(id) {
			return Boolean(selected);
		}
		function edgeMuted(from, to) {
			return Boolean(selected);
		}
		zoom().scaleExtent([.65, 2.8]).on("zoom", (event) => {
			transform = event.transform;
		});
		$: processes = radial(graph.processes ?? [], 250);
		$: interfaces = radial(graph.interfaces ?? [], 112);
		$: positioned = [...processes, ...interfaces];
		$: byId = new Map(positioned.map((item) => [item.id, item]));
		$: connected = /* @__PURE__ */ new Set();
		$: selectedNode = positioned.find((item) => item.id === selected);
		$$renderer.push(`<div class="atlas-toolbar segmented" role="tablist" aria-label="Atlas mode"><!--[-->`);
		const each_array = ensure_array_like([
			"structure",
			"live",
			"flow"
		]);
		for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
			let item = each_array[$$index];
			$$renderer.push(`<button${attr_class("", void 0, { "active": mode === item })}>${escape_html(item[0].toUpperCase() + item.slice(1))}</button>`);
		}
		$$renderer.push(`<!--]--></div> <div class="atlas-stage glass"><svg viewBox="0 0 1000 660" role="img" aria-label="Process Model network"><g${attr("transform", `translate(${transform.x} ${transform.y}) scale(${transform.k})`)}><!--[-->`);
		const each_array_1 = ensure_array_like(graph.edges);
		for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
			let edge = each_array_1[$$index_1];
			const from = byId.get(edge.from);
			const to = byId.get(edge.to);
			if (from && to) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<path${attr_class(`atlas-edge ${stringify(edge.kind)}`, void 0, { "muted": edgeMuted(edge.from, edge.to) })}${attr("d", `M ${from.x} ${from.y} Q ${center.x} ${center.y} ${to.x} ${to.y}`)}><title>${escape_html(edge.kind)}</title></path>`);
			} else $$renderer.push("<!--[-1-->");
			$$renderer.push(`<!--]-->`);
		}
		$$renderer.push(`<!--]--><!--[-->`);
		const each_array_2 = ensure_array_like(processes);
		for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
			let node = each_array_2[$$index_2];
			$$renderer.push(`<g${attr_class("atlas-node process", void 0, {
				"muted": muted(node.id),
				"selected": selected === node.id
			})}${attr("transform", `translate(${node.x} ${node.y})`)} role="button" tabindex="0"><circle r="34"></circle><text y="55">${escape_html(node.name)}</text></g>`);
		}
		$$renderer.push(`<!--]--><!--[-->`);
		const each_array_3 = ensure_array_like(interfaces);
		for (let $$index_3 = 0, $$length = each_array_3.length; $$index_3 < $$length; $$index_3++) {
			let node = each_array_3[$$index_3];
			$$renderer.push(`<g${attr_class("atlas-node interface", void 0, {
				"muted": muted(node.id),
				"selected": selected === node.id
			})}${attr("transform", `translate(${node.x} ${node.y})`)} role="button" tabindex="0"><circle r="25"></circle><text y="4">${escape_html(node.name.length > 15 ? `${node.name.slice(0, 14)}…` : node.name)}</text></g>`);
		}
		$$renderer.push(`<!--]-->`);
		if (mode !== "structure") {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<!--[-->`);
			const each_array_4 = ensure_array_like(graph.live ?? []);
			for (let $$index_4 = 0, $$length = each_array_4.length; $$index_4 < $$length; $$index_4++) {
				let item = each_array_4[$$index_4];
				const node = byId.get(item.processId);
				if (node) {
					$$renderer.push("<!--[0-->");
					$$renderer.push(`<circle${attr_class("live-dot", void 0, { "attention": item.attention })}${attr("cx", node.x + 24)}${attr("cy", node.y - 24)} r="7"><title>${escape_html(item.state)}</title></circle>`);
				} else $$renderer.push("<!--[-1-->");
				$$renderer.push(`<!--]-->`);
			}
			$$renderer.push(`<!--]-->`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]-->`);
		if (mode === "flow") {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<!--[-->`);
			const each_array_5 = ensure_array_like(graph.flow ?? []);
			for (let $$index_5 = 0, $$length = each_array_5.length; $$index_5 < $$length; $$index_5++) {
				let item = each_array_5[$$index_5];
				const node = byId.get(item.interfaceId ?? item.from ?? "");
				if (node) {
					$$renderer.push("<!--[0-->");
					$$renderer.push(`<circle class="flow-dot"${attr("cx", node.x)}${attr("cy", node.y - 34)} r="5"><title>${escape_html(item.status)}</title></circle>`);
				} else $$renderer.push("<!--[-1-->");
				$$renderer.push(`<!--]-->`);
			}
			$$renderer.push(`<!--]-->`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--></g></svg> <button class="atlas-mark" aria-label="Reset Atlas view"><img src="/assets/icon.svg" alt="ALPS"/></button> `);
		if (selectedNode) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<aside class="atlas-inspector glass-soft">`);
			Badge($$renderer, {
				tone: selectedNode.kind === "process" ? "info" : "neutral",
				children: ($$renderer) => {
					$$renderer.push(`<!---->${escape_html(selectedNode.kind)}`);
				},
				$$slots: { default: true }
			});
			$$renderer.push(`<!----> <h2>${escape_html(selectedNode.name)}</h2> `);
			if (selectedNode.revisionId) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<p>Revision ${escape_html(selectedNode.revisionId)}</p>`);
			} else $$renderer.push("<!--[-1-->");
			$$renderer.push(`<!--]--> <p>${escape_html(connected.size - 1)} connected element${escape_html(connected.size - 1 === 1 ? "" : "s")}</p> <button class="icon-close" aria-label="Close inspector">×</button></aside>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--></div>`);
		bind_props($$props, {
			graph,
			mode,
			onMode
		});
	});
}
//#endregion
//#region src/routes/atlas/+page.svelte
function _page($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let mode = "structure";
		const graph = createQuery(() => ({
			queryKey: ["graph", mode],
			queryFn: () => api(`/process-models/current/graph?mode=${mode}`)
		}));
		head("1wy8qhs", $$renderer, ($$renderer) => {
			$$renderer.title(($$renderer) => {
				$$renderer.push(`<title>Atlas · ALPS Local Runtime</title>`);
			});
		});
		if (graph.isPending) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<div class="empty-state">Resolving Process Model…</div>`);
		} else if (graph.isError) {
			$$renderer.push("<!--[1-->");
			$$renderer.push(`<div class="empty-state error">${escape_html(graph.error.message)}</div>`);
		} else if (graph.data) {
			$$renderer.push("<!--[2-->");
			AtlasCanvas($$renderer, {
				graph: graph.data,
				mode,
				onMode: (value) => mode = value
			});
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]-->`);
	});
}
//#endregion
export { _page as default };
