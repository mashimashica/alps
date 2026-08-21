import { S as getContext, d as derived, w as setContext } from "./index-server.js";
import { QueryObserver } from "@tanstack/query-core";
//#region node_modules/@tanstack/svelte-query/dist/context.js
var _contextKey = Symbol("QueryClient");
/** Retrieves a Client from Svelte's context */
var getQueryClientContext = () => {
	const client = getContext(_contextKey);
	if (!client) throw new Error("No QueryClient was found in Svelte context. Did you forget to wrap your component with QueryClientProvider?");
	return client;
};
/** Sets a QueryClient on Svelte's context */
var setQueryClientContext = (client) => {
	setContext(_contextKey, client);
};
var _isRestoringContextKey = Symbol("isRestoring");
/** Retrieves a `isRestoring` from Svelte's context */
var getIsRestoringContext = () => {
	try {
		return getContext(_isRestoringContextKey) ?? { current: false };
	} catch (error) {
		return { current: false };
	}
};
/** Sets a `isRestoring` on Svelte's context */
var setIsRestoringContext = (isRestoring) => {
	setContext(_isRestoringContextKey, isRestoring);
};
//#endregion
//#region node_modules/@tanstack/svelte-query/dist/useIsRestoring.js
function useIsRestoring() {
	return getIsRestoringContext();
}
//#endregion
//#region node_modules/@tanstack/svelte-query/dist/useQueryClient.js
function useQueryClient(queryClient) {
	if (queryClient) return queryClient;
	return getQueryClientContext();
}
globalThis.Date;
var SvelteSet = globalThis.Set;
var SvelteMap = globalThis.Map;
globalThis.URL;
globalThis.URLSearchParams;
/**
* @param {any} _
*/
function createSubscriber(_) {
	return () => {};
}
//#endregion
//#region node_modules/@tanstack/svelte-query/dist/containers.svelte.js
var __classPrivateFieldSet = function(receiver, state, value, kind, f) {
	if (kind === "m") throw new TypeError("Private method is not writable");
	if (kind === "a" && !f) throw new TypeError("Private accessor was defined without a setter");
	if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
	return kind === "a" ? f.call(receiver, value) : f ? f.value = value : state.set(receiver, value), value;
};
var __classPrivateFieldGet = function(receiver, state, kind, f) {
	if (kind === "a" && !f) throw new TypeError("Private accessor was defined without a getter");
	if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
	return kind === "m" ? f : kind === "a" ? f.call(receiver) : f ? f.value : state.get(receiver);
};
var _ReactiveValue_fn;
var _ReactiveValue_subscribe;
var ReactiveValue = class {
	constructor(fn, onSubscribe) {
		_ReactiveValue_fn.set(this, void 0);
		_ReactiveValue_subscribe.set(this, void 0);
		__classPrivateFieldSet(this, _ReactiveValue_fn, fn, "f");
		__classPrivateFieldSet(this, _ReactiveValue_subscribe, createSubscriber((update) => onSubscribe(update)), "f");
	}
	get current() {
		__classPrivateFieldGet(this, _ReactiveValue_subscribe, "f").call(this);
		return __classPrivateFieldGet(this, _ReactiveValue_fn, "f").call(this);
	}
};
_ReactiveValue_fn = /* @__PURE__ */ new WeakMap(), _ReactiveValue_subscribe = /* @__PURE__ */ new WeakMap();
/**
* Makes all of the top-level keys of an object into $state.raw fields whose initial values
* are the same as in the original object. Does not mutate the original object. Provides an `update`
* function that _can_ (but does not have to be) be used to replace all of the object's top-level keys
* with the values of the new object, while maintaining the original root object's reference.
*/
function createRawRef(init) {
	const refObj = Array.isArray(init) ? [] : {};
	const hiddenKeys = new SvelteSet();
	const out = new Proxy(refObj, {
		set(target, prop, value, receiver) {
			hiddenKeys.delete(prop);
			if (prop in target) return Reflect.set(target, prop, value, receiver);
			let state = value;
			Object.defineProperty(target, prop, {
				configurable: true,
				enumerable: true,
				get: () => {
					return state && isBranded(state) ? state() : state;
				},
				set: (v) => {
					state = v;
				}
			});
			return true;
		},
		has: (target, prop) => {
			if (hiddenKeys.has(prop)) return false;
			return prop in target;
		},
		ownKeys(target) {
			return Reflect.ownKeys(target).filter((key) => !hiddenKeys.has(key));
		},
		getOwnPropertyDescriptor(target, prop) {
			if (hiddenKeys.has(prop)) return;
			return Reflect.getOwnPropertyDescriptor(target, prop);
		},
		deleteProperty(target, prop) {
			if (prop in target) {
				target[prop] = void 0;
				hiddenKeys.add(prop);
				if (Array.isArray(target)) target.length--;
				return true;
			}
			return false;
		}
	});
	function update(newValue) {
		const existingKeys = Object.keys(out);
		const newKeys = Object.keys(newValue);
		const keysToRemove = existingKeys.filter((key) => !newKeys.includes(key));
		for (const key of keysToRemove) delete out[key];
		for (const key of newKeys) out[key] = brand(() => newValue[key]);
	}
	update(init);
	return [out, update];
}
var lazyBrand = Symbol("LazyValue");
function brand(fn) {
	fn[lazyBrand] = true;
	return fn;
}
function isBranded(fn) {
	return Boolean(fn[lazyBrand]);
}
//#endregion
//#region node_modules/@tanstack/svelte-query/dist/utils.svelte.js
var watchChanges = (sources, flush, effect) => {};
//#endregion
//#region node_modules/@tanstack/svelte-query/dist/createBaseQuery.svelte.js
function createBaseQuery(options, Observer, queryClient) {
	/** Load query client */
	const client = derived(() => useQueryClient(queryClient?.()));
	const isRestoring = useIsRestoring();
	const resolvedOptions = derived(() => {
		const opts = client().defaultQueryOptions(options());
		opts._optimisticResults = isRestoring.current ? "isRestoring" : "optimistic";
		return opts;
	});
	/** Creates the observer */
	let observer = new Observer(client(), resolvedOptions());
	function createResult() {
		const result = observer.getOptimisticResult(resolvedOptions());
		return !resolvedOptions().notifyOnChangeProps ? observer.trackResult(result) : result;
	}
	const [query, update] = createRawRef(createResult());
	return query;
}
//#endregion
//#region node_modules/@tanstack/svelte-query/dist/createQuery.js
function createQuery(options, queryClient) {
	return createBaseQuery(options, QueryObserver, queryClient);
}
//#endregion
export { createRawRef as a, useQueryClient as c, getQueryClientContext as d, setIsRestoringContext as f, ReactiveValue as i, useIsRestoring as l, createBaseQuery as n, SvelteMap as o, setQueryClientContext as p, watchChanges as r, createSubscriber as s, createQuery as t, getIsRestoringContext as u };
