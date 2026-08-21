import { E as escape_html, T as attr, f as ensure_array_like, p as head, u as bind_props, vt as fallback } from "../../../chunks/index-server.js";
import { c as useQueryClient, t as createQuery } from "../../../chunks/createQuery.js";
import { a as createMutation, i as Portal, n as Dialog, r as Dialog_overlay, t as Dialog_content } from "../../../chunks/dialog-content.js";
import { n as api, r as json, t as Badge } from "../../../chunks/Badge.js";
import { n as number, r as relativeTime, t as humanState } from "../../../chunks/format.js";
import { t as Button } from "../../../chunks/Button.js";
//#region src/lib/components/DecisionDialog.svelte
function DecisionDialog($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let open = fallback($$props["open"], false);
		let gate = $$props["gate"];
		let run = $$props["run"];
		let afterDecision = fallback($$props["afterDecision"], () => void 0);
		const client = useQueryClient();
		let rationale = "";
		const mutation = createMutation(() => ({
			mutationFn: (decision) => api(`/gates/${gate?.id}/decisions`, json("POST", {
				decision,
				actor: "local-user",
				authority: "operator",
				rationale,
				expectedVersion: run?.version
			})),
			onSuccess: async () => {
				await client.invalidateQueries({ queryKey: ["runs"] });
				await client.invalidateQueries({ queryKey: ["gates"] });
				if (run?.id) await client.invalidateQueries({ queryKey: ["run", run.id] });
				open = false;
				rationale = "";
				afterDecision();
			}
		}));
		let $$settled = true;
		let $$inner_renderer;
		function $$render_inner($$renderer) {
			Dialog($$renderer, {
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
								class: "dialog-content decision-dialog",
								"aria-label": "Human Decision",
								children: ($$renderer) => {
									if (gate && run) {
										$$renderer.push("<!--[0-->");
										$$renderer.push(`<header class="decision-header">`);
										Badge($$renderer, {
											tone: "danger",
											children: ($$renderer) => {
												$$renderer.push(`<!---->Human decision`);
											},
											$$slots: { default: true }
										});
										$$renderer.push(`<!----><button class="icon-close" aria-label="Close">×</button></header> <h2>${escape_html(gate.title)}</h2> <p class="decision-effect">${escape_html(gate.effect)}</p> <dl class="decision-facts"><div><dt>Run</dt><dd>${escape_html(run.title)} · version ${escape_html(run.version)}</dd></div> <div><dt>External effect</dt><dd>${escape_html(gate.externalEffect || "No external effect was declared.")}</dd></div> <div><dt>Reversibility</dt><dd>${escape_html(gate.reversible ? "Reversible" : "Irreversible")}</dd></div> <div><dt>Authority</dt><dd>${escape_html(gate.authority)}</dd></div></dl> `);
										if (gate.criteria?.length) {
											$$renderer.push("<!--[0-->");
											$$renderer.push(`<section class="decision-list"><h3>Criteria</h3><ul><!--[-->`);
											const each_array = ensure_array_like(gate.criteria);
											for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
												let item = each_array[$$index];
												$$renderer.push(`<li>${escape_html(item)}</li>`);
											}
											$$renderer.push(`<!--]--></ul></section>`);
										} else $$renderer.push("<!--[-1-->");
										$$renderer.push(`<!--]--> `);
										if (gate.unknown?.length) {
											$$renderer.push("<!--[0-->");
											$$renderer.push(`<section class="decision-list warning"><h3>Unknown</h3><ul><!--[-->`);
											const each_array_1 = ensure_array_like(gate.unknown);
											for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
												let item = each_array_1[$$index_1];
												$$renderer.push(`<li>${escape_html(item)}</li>`);
											}
											$$renderer.push(`<!--]--></ul></section>`);
										} else $$renderer.push("<!--[-1-->");
										$$renderer.push(`<!--]--> `);
										if (gate.evidence?.length) {
											$$renderer.push("<!--[0-->");
											$$renderer.push(`<section class="decision-list"><h3>Evidence</h3><ul><!--[-->`);
											const each_array_2 = ensure_array_like(gate.evidence);
											for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
												let item = each_array_2[$$index_2];
												$$renderer.push(`<li>${escape_html(item.note || item.artifactId || item.uri || item.digest)}</li>`);
											}
											$$renderer.push(`<!--]--></ul></section>`);
										} else $$renderer.push("<!--[-1-->");
										$$renderer.push(`<!--]--> <label class="field"><span>Rationale</span><textarea rows="3" placeholder="Record the basis for the Decision">`);
										const $$body = escape_html(rationale);
										if ($$body) $$renderer.push(`${$$body}`);
										$$renderer.push(`</textarea></label> `);
										if (mutation.isError) {
											$$renderer.push("<!--[0-->");
											$$renderer.push(`<p class="form-error">${escape_html(mutation.error.message)}</p>`);
										} else $$renderer.push("<!--[-1-->");
										$$renderer.push(`<!--]--> <footer class="decision-actions">`);
										Button($$renderer, {
											children: ($$renderer) => {
												$$renderer.push(`<!---->Hold`);
											},
											$$slots: { default: true }
										});
										$$renderer.push(`<!----> `);
										Button($$renderer, {
											children: ($$renderer) => {
												$$renderer.push(`<!---->Return for changes`);
											},
											$$slots: { default: true }
										});
										$$renderer.push(`<!----> `);
										Button($$renderer, {
											variant: "primary",
											children: ($$renderer) => {
												$$renderer.push(`<!---->Continue`);
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
			gate,
			run,
			afterDecision
		});
	});
}
//#endregion
//#region src/lib/components/RunSheet.svelte
function RunSheet($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let open = fallback($$props["open"], false);
		let runId = fallback($$props["runId"], "");
		let decisionOpen = false;
		const detail = createQuery(() => ({
			queryKey: ["run", runId],
			queryFn: () => api(`/runs/${runId}`),
			enabled: Boolean(open && runId)
		}));
		function outcomeTone(status) {
			return status === "assessed_achieved" ? "success" : status === "not_achieved" ? "danger" : status === "agent_reported" ? "info" : "neutral";
		}
		let $$settled = true;
		let $$inner_renderer;
		function $$render_inner($$renderer) {
			Dialog($$renderer, {
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
								class: "dialog-content run-sheet",
								"aria-label": "Run detail",
								children: ($$renderer) => {
									if (detail.isPending) {
										$$renderer.push("<!--[0-->");
										$$renderer.push(`<div class="empty-state">Loading Run…</div>`);
									} else if (detail.isError) {
										$$renderer.push("<!--[1-->");
										$$renderer.push(`<div class="empty-state error">${escape_html(detail.error.message)}</div>`);
									} else if (detail.data) {
										$$renderer.push("<!--[2-->");
										$$renderer.push(`<header class="viewer-header"><div class="viewer-identity"><span class="asset-icon">R</span><div><h2>${escape_html(detail.data.run.title)}</h2><p>${escape_html(detail.data.run.process)} · ${escape_html(humanState(detail.data.run.state))}</p></div></div> <button class="icon-close" aria-label="Close">×</button></header> <div class="run-sheet-content">`);
										if (detail.data.gate) {
											$$renderer.push("<!--[0-->");
											$$renderer.push(`<button class="attention-action"><span>Decision required</span><strong>${escape_html(detail.data.gate.title)}</strong></button>`);
										} else $$renderer.push("<!--[-1-->");
										$$renderer.push(`<!--]--> <section class="run-section"><h3>Outcomes</h3> `);
										if (detail.data.outcomes?.length) {
											$$renderer.push("<!--[0-->");
											$$renderer.push(`<div class="outcome-list"><!--[-->`);
											const each_array = ensure_array_like(detail.data.outcomes);
											for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
												let outcome = each_array[$$index];
												$$renderer.push(`<div>`);
												Badge($$renderer, {
													tone: outcomeTone(outcome.status),
													children: ($$renderer) => {
														$$renderer.push(`<!---->${escape_html(humanState(outcome.status))}`);
													},
													$$slots: { default: true }
												});
												$$renderer.push(`<!----><span>${escape_html(outcome.name)}</span></div>`);
											}
											$$renderer.push(`<!--]--></div>`);
										} else {
											$$renderer.push("<!--[-1-->");
											$$renderer.push(`<p class="muted">No Outcomes were declared for this Run.</p>`);
										}
										$$renderer.push(`<!--]--></section> <section class="run-section"><h3>Effective context</h3><dl class="context-grid"><div><dt>Process revision</dt><dd>${escape_html(detail.data.run.processRevisionId || "—")}</dd></div><div><dt>Skill package</dt><dd>${escape_html(detail.data.run.skillPackageRevisionId || "—")}</dd></div><div><dt>Process Model</dt><dd>${escape_html(detail.data.run.processModelRevisionId || "—")}</dd></div><div><dt>Actor</dt><dd>${escape_html(detail.data.run.actor?.type || "system")} · ${escape_html(detail.data.run.actor?.channel || "internal")}</dd></div></dl></section> <section class="run-section"><h3>Artifacts and Handoffs</h3><div class="compact-list"><!--[-->`);
										const each_array_1 = ensure_array_like(detail.data.artifacts ?? []);
										for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
											let artifact = each_array_1[$$index_1];
											$$renderer.push(`<div><strong>${escape_html(artifact.name)}</strong><span>${escape_html(artifact.role || artifact.mediaType)} · ${escape_html(number(artifact.size))} bytes</span></div>`);
										}
										$$renderer.push(`<!--]--><!--[-->`);
										const each_array_2 = ensure_array_like(detail.data.handoffs ?? []);
										for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
											let handoff = each_array_2[$$index_2];
											$$renderer.push(`<div><strong>Handoff</strong><span>${escape_html(String(handoff.status ?? ""))} · ${escape_html(String(handoff.recipientInput ?? ""))}</span></div>`);
										}
										$$renderer.push(`<!--]-->`);
										if (!(detail.data.artifacts?.length || detail.data.handoffs?.length)) {
											$$renderer.push("<!--[0-->");
											$$renderer.push(`<p class="muted">No Artifacts or Handoffs.</p>`);
										} else $$renderer.push("<!--[-1-->");
										$$renderer.push(`<!--]--></div></section> <section class="run-section"><h3>Model and usage</h3><div class="compact-list"><!--[-->`);
										const each_array_3 = ensure_array_like(detail.data.modelInvocations ?? []);
										for (let $$index_3 = 0, $$length = each_array_3.length; $$index_3 < $$length; $$index_3++) {
											let invocation = each_array_3[$$index_3];
											$$renderer.push(`<div><strong>${escape_html(String(invocation.resolved?.modelRaw ?? invocation.requested?.modelRaw ?? "Model invocation"))}</strong><span>${escape_html(String(invocation.role ?? "main"))}</span></div>`);
										}
										$$renderer.push(`<!--]--><!--[-->`);
										const each_array_4 = ensure_array_like(detail.data.usageObservations ?? []);
										for (let $$index_4 = 0, $$length = each_array_4.length; $$index_4 < $$length; $$index_4++) {
											let observation = each_array_4[$$index_4];
											$$renderer.push(`<div><strong>${escape_html(String(observation.status ?? "usage"))}</strong><span>${escape_html(String(observation.accountingBasis ?? observation.source ?? "reported"))}</span></div>`);
										}
										$$renderer.push(`<!--]-->`);
										if (!(detail.data.modelInvocations?.length || detail.data.usageObservations?.length)) {
											$$renderer.push("<!--[0-->");
											$$renderer.push(`<p class="muted">No model usage was reported.</p>`);
										} else $$renderer.push("<!--[-1-->");
										$$renderer.push(`<!--]--></div></section> <section class="run-section"><h3>Timeline</h3><div class="timeline"><!--[-->`);
										const each_array_5 = ensure_array_like(detail.data.events ?? []);
										for (let $$index_5 = 0, $$length = each_array_5.length; $$index_5 < $$length; $$index_5++) {
											let event = each_array_5[$$index_5];
											$$renderer.push(`<div><span class="event-dot"></span><div><strong>${escape_html(event.eventType)}</strong><small>${escape_html(relativeTime(event.occurredAt))}</small></div></div>`);
										}
										$$renderer.push(`<!--]--></div></section></div> `);
										DecisionDialog($$renderer, {
											gate: detail.data.gate,
											run: detail.data.run,
											afterDecision: () => detail.refetch(),
											get open() {
												return decisionOpen;
											},
											set open($$value) {
												decisionOpen = $$value;
												$$settled = false;
											}
										});
										$$renderer.push(`<!---->`);
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
			runId
		});
	});
}
//#endregion
//#region src/routes/runs/+page.svelte
function _page($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let lanes;
		let sheetOpen = false;
		let selectedRun = "";
		let createOpen = false;
		let title = "";
		let process = "Apply Skills";
		const client = useQueryClient();
		const runs = createQuery(() => ({
			queryKey: ["runs"],
			queryFn: () => api("/runs")
		}));
		const gates = createQuery(() => ({
			queryKey: ["gates"],
			queryFn: () => api("/gates")
		}));
		const createRun = createMutation(() => ({
			mutationFn: () => api("/runs", json("POST", {
				title,
				process
			})),
			onSuccess: async (run) => {
				createOpen = false;
				title = "";
				await client.invalidateQueries({ queryKey: ["runs"] });
				selectedRun = run.id;
				sheetOpen = true;
			}
		}));
		function openGate(run) {
			return (gates.data ?? []).find((gate) => gate.runId === run.id);
		}
		$: lanes = {
			Now: (runs.data ?? []).filter((run) => ["created", "active"].includes(run.state)),
			Waiting: (runs.data ?? []).filter((run) => run.state.startsWith("waiting_") || run.state === "completion_requested"),
			Done: (runs.data ?? []).filter((run) => [
				"completed",
				"failed",
				"cancelled"
			].includes(run.state))
		};
		let $$settled = true;
		let $$inner_renderer;
		function $$render_inner($$renderer) {
			head("1btsuzj", $$renderer, ($$renderer) => {
				$$renderer.title(($$renderer) => {
					$$renderer.push(`<title>Runs · ALPS Local Runtime</title>`);
				});
			});
			$$renderer.push(`<div class="page-actions">`);
			Button($$renderer, {
				variant: "primary",
				children: ($$renderer) => {
					$$renderer.push(`<!---->Start Run`);
				},
				$$slots: { default: true }
			});
			$$renderer.push(`<!----></div> `);
			if (runs.isPending) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<div class="empty-state">Loading Runs…</div>`);
			} else if (runs.isError) {
				$$renderer.push("<!--[1-->");
				$$renderer.push(`<div class="empty-state error">${escape_html(runs.error.message)}</div>`);
			} else {
				$$renderer.push("<!--[-1-->");
				$$renderer.push(`<div class="run-board"><!--[-->`);
				const each_array = ensure_array_like(Object.entries(lanes));
				for (let $$index_1 = 0, $$length = each_array.length; $$index_1 < $$length; $$index_1++) {
					let [lane, items] = each_array[$$index_1];
					$$renderer.push(`<section class="run-lane"><header><h2>${escape_html(lane)}</h2><span>${escape_html(items.length)}</span></header><div class="run-cards">`);
					const each_array_1 = ensure_array_like(items);
					if (each_array_1.length !== 0) {
						$$renderer.push("<!--[-->");
						for (let $$index = 0, $$length = each_array_1.length; $$index < $$length; $$index++) {
							let run = each_array_1[$$index];
							$$renderer.push(`<button class="run-card glass-soft"><h3>${escape_html(run.title)}</h3><p>${escape_html(run.statusText || humanState(run.state))}</p> `);
							if (run.progress != null) {
								$$renderer.push("<!--[0-->");
								$$renderer.push(`<progress${attr("value", run.progress)} max="100"></progress>`);
							} else $$renderer.push("<!--[-1-->");
							$$renderer.push(`<!--]--> <footer>`);
							if (openGate(run)) {
								$$renderer.push("<!--[0-->");
								Badge($$renderer, {
									tone: "danger",
									children: ($$renderer) => {
										$$renderer.push(`<!---->Decision`);
									},
									$$slots: { default: true }
								});
							} else {
								$$renderer.push("<!--[-1-->");
								$$renderer.push(`<span>${escape_html(run.process)}</span>`);
							}
							$$renderer.push(`<!--]--><span>${escape_html(relativeTime(run.updatedAt))}</span></footer></button>`);
						}
					} else {
						$$renderer.push("<!--[!-->");
						$$renderer.push(`<div class="lane-empty">No Runs</div>`);
					}
					$$renderer.push(`<!--]--></div></section>`);
				}
				$$renderer.push(`<!--]--></div>`);
			}
			$$renderer.push(`<!--]--> `);
			RunSheet($$renderer, {
				runId: selectedRun,
				get open() {
					return sheetOpen;
				},
				set open($$value) {
					sheetOpen = $$value;
					$$settled = false;
				}
			});
			$$renderer.push(`<!----> `);
			Dialog($$renderer, {
				get open() {
					return createOpen;
				},
				set open($$value) {
					createOpen = $$value;
					$$settled = false;
				},
				children: ($$renderer) => {
					Portal($$renderer, {
						children: ($$renderer) => {
							Dialog_overlay($$renderer, { class: "dialog-overlay" });
							$$renderer.push(`<!---->`);
							Dialog_content($$renderer, {
								class: "dialog-content form-dialog",
								"aria-label": "Start Run",
								children: ($$renderer) => {
									$$renderer.push(`<header><h2>Start Run</h2><button class="icon-close" aria-label="Close">×</button></header> <label class="field"><span>Title</span><input${attr("value", title)} placeholder="Describe the work"/></label> <label class="field"><span>Process or Skill</span><input${attr("value", process)}/></label> `);
									if (createRun.isError) {
										$$renderer.push("<!--[0-->");
										$$renderer.push(`<p class="form-error">${escape_html(createRun.error.message)}</p>`);
									} else $$renderer.push("<!--[-1-->");
									$$renderer.push(`<!--]--> <footer>`);
									Button($$renderer, {
										children: ($$renderer) => {
											$$renderer.push(`<!---->Cancel`);
										},
										$$slots: { default: true }
									});
									$$renderer.push(`<!---->`);
									Button($$renderer, {
										variant: "primary",
										disabled: !title.trim(),
										children: ($$renderer) => {
											$$renderer.push(`<!---->Start Run`);
										},
										$$slots: { default: true }
									});
									$$renderer.push(`<!----></footer>`);
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
