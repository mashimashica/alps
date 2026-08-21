import { Ct as __reExport, E as escape_html, S as getContext, St as __exportAll, T as attr, b as unsubscribe_stores, d as derived, f as ensure_array_like, g as slot, r as onDestroy, s as attr_class, u as bind_props, v as store_get, vt as fallback } from "../../chunks/index-server.js";
import { a as createRawRef, c as useQueryClient, d as getQueryClientContext, f as setIsRestoringContext, i as ReactiveValue, l as useIsRestoring, n as createBaseQuery, p as setQueryClientContext, t as createQuery, u as getIsRestoringContext } from "../../chunks/createQuery.js";
import { a as createMutation, i as Portal, n as Dialog, r as Dialog_overlay, t as Dialog_content } from "../../chunks/dialog-content.js";
import "../../chunks/client.js";
import "../../chunks/navigation.js";
import { InfiniteQueryObserver, QueriesObserver, QueryClient, hydrate } from "@tanstack/query-core";
//#region node_modules/@tanstack/svelte-query/dist/queryOptions.js
function queryOptions(options) {
	return options;
}
//#endregion
//#region node_modules/@tanstack/svelte-query/dist/createQueries.svelte.js
function createQueries(createQueriesOptions, queryClient) {
	const client = derived(() => useQueryClient(queryClient?.()));
	const isRestoring = useIsRestoring();
	const $$d = derived(createQueriesOptions), queries = derived(() => $$d().queries), combine = derived(() => $$d().combine);
	const resolvedQueryOptions = derived(() => queries().map((opts) => {
		const resolvedOptions = client().defaultQueryOptions(opts);
		resolvedOptions._optimisticResults = isRestoring.current ? "isRestoring" : "optimistic";
		return resolvedOptions;
	}));
	const observer = derived(() => new QueriesObserver(client(), resolvedQueryOptions(), combine()));
	function createResult() {
		const [_, getCombinedResult, trackResult] = observer().getOptimisticResult(resolvedQueryOptions(), combine());
		return getCombinedResult(trackResult());
	}
	const [results, update] = createRawRef(createResult());
	return results;
}
//#endregion
//#region node_modules/@tanstack/svelte-query/dist/createInfiniteQuery.js
function createInfiniteQuery(options, queryClient) {
	return createBaseQuery(options, InfiniteQueryObserver, queryClient);
}
//#endregion
//#region node_modules/@tanstack/svelte-query/dist/infiniteQueryOptions.js
function infiniteQueryOptions(options) {
	return options;
}
//#endregion
//#region node_modules/@tanstack/svelte-query/dist/mutationOptions.js
function mutationOptions(options) {
	return options;
}
//#endregion
//#region node_modules/@tanstack/svelte-query/dist/useMutationState.svelte.js
function getResult(mutationCache, options) {
	return mutationCache.findAll(options.filters).map((mutation) => options.select ? options.select(mutation) : mutation.state);
}
function useMutationState(options = {}, queryClient) {
	return getResult(useQueryClient(queryClient).getMutationCache(), options);
}
//#endregion
//#region node_modules/@tanstack/svelte-query/dist/useIsFetching.svelte.js
function useIsFetching(filters, queryClient) {
	const client = useQueryClient(queryClient);
	const queryCache = client.getQueryCache();
	return new ReactiveValue(() => client.isFetching(filters), (update) => queryCache.subscribe(update));
}
//#endregion
//#region node_modules/@tanstack/svelte-query/dist/useIsMutating.svelte.js
function useIsMutating(filters, queryClient) {
	const client = useQueryClient(queryClient);
	const cache = client.getMutationCache();
	return new ReactiveValue(() => client.isMutating(filters), (update) => cache.subscribe(update));
}
//#endregion
//#region node_modules/@tanstack/svelte-query/dist/useHydrate.js
function useHydrate(state, options, queryClient) {
	const client = useQueryClient(queryClient);
	if (state) hydrate(client, state, options);
}
//#endregion
//#region node_modules/@tanstack/svelte-query/dist/HydrationBoundary.svelte
function HydrationBoundary($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		const { children, state, options = void 0, queryClient = void 0 } = $$props;
		useHydrate(state, options, queryClient);
		children($$renderer);
		$$renderer.push(`<!---->`);
	});
}
//#endregion
//#region node_modules/@tanstack/svelte-query/dist/QueryClientProvider.svelte
function QueryClientProvider($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		const { client = new QueryClient(), children } = $$props;
		setQueryClientContext(client);
		onDestroy(() => {
			client.unmount();
		});
		children($$renderer);
		$$renderer.push(`<!---->`);
	});
}
//#endregion
//#region node_modules/@tanstack/svelte-query/dist/index.js
var dist_exports = /* @__PURE__ */ __exportAll({
	HydrationBoundary: () => HydrationBoundary,
	QueryClientProvider: () => QueryClientProvider,
	createInfiniteQuery: () => createInfiniteQuery,
	createMutation: () => createMutation,
	createQueries: () => createQueries,
	createQuery: () => createQuery,
	getIsRestoringContext: () => getIsRestoringContext,
	getQueryClientContext: () => getQueryClientContext,
	infiniteQueryOptions: () => infiniteQueryOptions,
	mutationOptions: () => mutationOptions,
	queryOptions: () => queryOptions,
	setIsRestoringContext: () => setIsRestoringContext,
	setQueryClientContext: () => setQueryClientContext,
	useHydrate: () => useHydrate,
	useIsFetching: () => useIsFetching,
	useIsMutating: () => useIsMutating,
	useIsRestoring: () => useIsRestoring,
	useMutationState: () => useMutationState,
	useQueryClient: () => useQueryClient
});
import * as import__tanstack_query_core from "@tanstack/query-core";
__reExport(dist_exports, import__tanstack_query_core);
/* istanbul ignore file */
//#endregion
//#region node_modules/@sveltejs/kit/src/runtime/app/stores.js
/**
* A function that returns all of the contextual stores. On the server, this must be called during component initialization.
* Only use this if you need to defer store subscription until after the component has mounted, for some reason.
*
* @deprecated Use `$app/state` instead (requires Svelte 5, [see docs for more info](https://svelte.dev/docs/kit/migrating-to-sveltekit-2#SvelteKit-2.12:-$app-stores-deprecated))
*/
var getStores = () => {
	const stores$1 = getContext("__svelte__");
	return {
		/** @type {typeof page} */
		page: { subscribe: stores$1.page.subscribe },
		/** @type {typeof navigating} */
		navigating: { subscribe: stores$1.navigating.subscribe },
		/** @type {typeof updated} */
		updated: stores$1.updated
	};
};
/**
* A readable store whose value contains page data.
*
* On the server, this store can only be subscribed to during component initialization. In the browser, it can be subscribed to at any time.
*
* @deprecated Use `page` from `$app/state` instead (requires Svelte 5, [see docs for more info](https://svelte.dev/docs/kit/migrating-to-sveltekit-2#SvelteKit-2.12:-$app-stores-deprecated))
* @type {import('svelte/store').Readable<import('@sveltejs/kit').Page>}
*/
var page = { subscribe(fn) {
	return getStores().page.subscribe(fn);
} };
//#endregion
//#region src/lib/components/AppRail.svelte
function AppRail($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		var $$store_subs;
		const links = [
			{
				href: "/atlas",
				label: "Atlas",
				icon: "◉"
			},
			{
				href: "/runs",
				label: "Runs",
				icon: "▦"
			},
			{
				href: "/library",
				label: "Library",
				icon: "◇"
			},
			{
				href: "/analysis",
				label: "Analysis",
				icon: "⌁"
			}
		];
		$$renderer.push(`<aside class="rail glass" aria-label="Primary navigation"><a class="brand" href="/atlas" aria-label="ALPS"><img src="/assets/icon.svg" alt=""/></a> <!--[-->`);
		const each_array = ensure_array_like(links);
		for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
			let link = each_array[$$index];
			$$renderer.push(`<a${attr_class("nav-item", void 0, { "active": store_get($$store_subs ??= {}, "$page", page).url.pathname.startsWith(link.href) })}${attr("href", link.href)}${attr("aria-label", link.label)}${attr("title", link.label)}><span aria-hidden="true">${escape_html(link.icon)}</span></a>`);
		}
		$$renderer.push(`<!--]--></aside>`);
		if ($$store_subs) unsubscribe_stores($$store_subs);
	});
}
//#endregion
//#region src/lib/components/CommandPalette.svelte
function CommandPalette($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let visible;
		let open = fallback($$props["open"], false);
		const routes = [
			{
				href: "/atlas",
				name: "Atlas",
				detail: "Process and interface structure"
			},
			{
				href: "/runs",
				name: "Runs",
				detail: "Work and human attention"
			},
			{
				href: "/library",
				name: "Library",
				detail: "Skills, Plugins, and Models"
			},
			{
				href: "/analysis",
				name: "Analysis",
				detail: "Flow, quality, oversight, and usage"
			}
		];
		let search = "";
		$: visible = routes.filter((item) => `${item.name} ${item.detail}`.toLowerCase().includes(search.toLowerCase()));
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
								class: "dialog-content command-dialog",
								"aria-label": "Command palette",
								children: ($$renderer) => {
									$$renderer.push(`<input class="command-input"${attr("value", search)} placeholder="Search or go to…"/> <div class="command-results"><!--[-->`);
									const each_array = ensure_array_like(visible);
									for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
										let item = each_array[$$index];
										$$renderer.push(`<button class="command-item"><strong>${escape_html(item.name)}</strong><span>${escape_html(item.detail)}</span></button>`);
									}
									$$renderer.push(`<!--]--></div>`);
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
		bind_props($$props, { open });
	});
}
//#endregion
//#region src/lib/components/AppShell.svelte
function AppShell($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		var $$store_subs;
		let key, meta;
		let commandOpen = false;
		const metadata = {
			atlas: ["Atlas", "Process and interface relationships"],
			runs: ["Runs", "Current work and human attention"],
			library: ["Library", "Skills, Plugins, and Process Models"],
			analysis: ["Analysis", "Operational evidence for improvement"]
		};
		$: key = store_get($$store_subs ??= {}, "$page", page).url.pathname.split("/")[1] || "atlas";
		$: meta = metadata[key] ?? metadata.atlas;
		let $$settled = true;
		let $$inner_renderer;
		function $$render_inner($$renderer) {
			$$renderer.push(`<div class="app-shell"${attr("data-ready", "false")}>`);
			AppRail($$renderer, {});
			$$renderer.push(`<!----> <main class="main-shell"><header class="topbar glass-soft"><div><h1>${escape_html(meta[0])}</h1><p>${escape_html(meta[1])}</p></div> <button class="command-trigger" aria-keyshortcuts="Control+K Meta+K">Search or go to… <kbd>⌘K</kbd></button></header> <div class="page-content"><!--[-->`);
			slot($$renderer, $$props, "default", {}, null);
			$$renderer.push(`<!--]--></div></main></div> `);
			CommandPalette($$renderer, {
				get open() {
					return commandOpen;
				},
				set open($$value) {
					commandOpen = $$value;
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
		if ($$store_subs) unsubscribe_stores($$store_subs);
	});
}
//#endregion
//#region src/routes/+layout.svelte
function _layout($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		QueryClientProvider($$renderer, {
			client: new dist_exports.QueryClient({ defaultOptions: { queries: {
				staleTime: 8e3,
				refetchOnWindowFocus: false
			} } }),
			children: ($$renderer) => {
				AppShell($$renderer, {
					children: ($$renderer) => {
						$$renderer.push(`<!--[-->`);
						slot($$renderer, $$props, "default", {}, null);
						$$renderer.push(`<!--]-->`);
					},
					$$slots: { default: true }
				});
			},
			$$slots: { default: true }
		});
	});
}
//#endregion
export { _layout as default };
