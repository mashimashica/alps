import { E as escape_html, T as attr, c as attr_style, f as ensure_array_like, p as head, s as attr_class } from "../../../chunks/index-server.js";
import { t as createQuery } from "../../../chunks/createQuery.js";
import { n as api, t as Badge } from "../../../chunks/Badge.js";
import { n as number } from "../../../chunks/format.js";
//#region src/routes/analysis/+page.svelte
function _page($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let lens = "flow";
		const analysis = createQuery(() => ({
			queryKey: ["analysis", lens],
			queryFn: () => api(`/analysis/${lens}`)
		}));
		function maxValue(points) {
			return Math.max(1, ...points.map((point) => point.value));
		}
		head("8pceb3", $$renderer, ($$renderer) => {
			$$renderer.title(($$renderer) => {
				$$renderer.push(`<title>Analysis · ALPS Local Runtime</title>`);
			});
		});
		$$renderer.push(`<div class="analysis-tabs segmented"><!--[-->`);
		const each_array = ensure_array_like([
			"flow",
			"quality",
			"oversight",
			"usage"
		]);
		for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
			let item = each_array[$$index];
			$$renderer.push(`<button${attr_class("", void 0, { "active": lens === item })}>${escape_html(item[0].toUpperCase() + item.slice(1))}</button>`);
		}
		$$renderer.push(`<!--]--></div> `);
		if (analysis.isPending) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<div class="empty-state">Building analytical projection…</div>`);
		} else if (analysis.isError) {
			$$renderer.push("<!--[1-->");
			$$renderer.push(`<div class="empty-state error">${escape_html(analysis.error.message)}</div>`);
		} else if (analysis.data) {
			$$renderer.push("<!--[2-->");
			$$renderer.push(`<section class="analysis-layout"><div class="metric-grid"><!--[-->`);
			const each_array_1 = ensure_array_like(analysis.data.metrics.slice(0, 3));
			for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
				let metric = each_array_1[$$index_1];
				$$renderer.push(`<article class="metric-card glass"><strong>${escape_html(number(metric.value))}</strong><h2>${escape_html(metric.label)}</h2><p>${escape_html(metric.definition)}</p><small>${escape_html(metric.coverage)}</small></article>`);
			}
			$$renderer.push(`<!--]--></div> <article class="analysis-chart panel glass"><header><div><h2>${escape_html(analysis.data.lens)} over time</h2><p>${escape_html(analysis.data.definition)}</p></div>`);
			Badge($$renderer, {
				tone: "neutral",
				children: ($$renderer) => {
					$$renderer.push(`<!---->${escape_html(analysis.data.mappingRevision)}`);
				},
				$$slots: { default: true }
			});
			$$renderer.push(`<!----></header> `);
			if (analysis.data.series?.[0]?.points?.length) {
				$$renderer.push("<!--[0-->");
				const series = analysis.data.series[0];
				const maximum = maxValue(series.points);
				$$renderer.push(`<div class="bars"${attr("aria-label", series.label)}><!--[-->`);
				const each_array_2 = ensure_array_like(series.points);
				for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
					let point = each_array_2[$$index_2];
					$$renderer.push(`<div class="bar-column"${attr("title", `${point.at}: ${point.value}`)}><div class="bar"${attr_style("", { height: `${Math.max(3, point.value / maximum * 100)}%` })}></div><span>${escape_html(point.at.slice(5, 10))}</span></div>`);
				}
				$$renderer.push(`<!--]--></div>`);
			} else {
				$$renderer.push("<!--[-1-->");
				$$renderer.push(`<div class="empty-state compact">No time series is available for this period.</div>`);
			}
			$$renderer.push(`<!--]--></article> <article class="findings panel glass"><h2>Findings</h2>`);
			const each_array_3 = ensure_array_like(analysis.data.findings.slice(0, 3));
			if (each_array_3.length !== 0) {
				$$renderer.push("<!--[-->");
				for (let $$index_3 = 0, $$length = each_array_3.length; $$index_3 < $$length; $$index_3++) {
					let finding = each_array_3[$$index_3];
					$$renderer.push(`<div class="finding">`);
					Badge($$renderer, {
						tone: finding.severity === "warning" ? "warning" : finding.severity === "error" ? "danger" : "info",
						children: ($$renderer) => {
							$$renderer.push(`<!---->${escape_html(finding.severity)}`);
						},
						$$slots: { default: true }
					});
					$$renderer.push(`<!----><div><strong>${escape_html(finding.title)}</strong><p>${escape_html(finding.detail)}</p></div></div>`);
				}
			} else {
				$$renderer.push("<!--[!-->");
				$$renderer.push(`<p class="muted">No actionable finding in the selected lens.</p>`);
			}
			$$renderer.push(`<!--]--></article></section>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]-->`);
	});
}
//#endregion
export { _page as default };
