import { C as hasContext, S as getContext, _ as spread_props, a as tick, d as derived, l as attributes, lt as ATTACHMENT_KEY, m as props_id, n as mount, o as unmount, u as bind_props, w as setContext, x as getAllContexts, xt as run } from "./index-server.js";
import { i as on } from "./legacy-client.js";
import { c as useQueryClient, o as SvelteMap, s as createSubscriber } from "./createQuery.js";
import { clsx } from "clsx";
import { MutationObserver as MutationObserver$1, noop } from "@tanstack/query-core";
import parse from "style-to-object";
import { focusable, isFocusable, tabbable } from "tabbable";
//#region node_modules/@tanstack/svelte-query/dist/createMutation.svelte.js
function createMutation(options, queryClient) {
	const client = derived(() => useQueryClient(queryClient?.()));
	let observer = new MutationObserver$1(client(), options());
	const mutate = (variables, mutateOptions) => {
		observer.mutate(variables, mutateOptions).catch(noop);
	};
	let result = observer.getCurrentResult();
	return derived(() => new Proxy(result, { get: (_, prop) => {
		const r = {
			...result,
			mutate,
			mutateAsync: result.mutate
		};
		if (prop == "value") return r;
		return r[prop];
	} }))();
}
//#endregion
//#region node_modules/svelte-toolbelt/dist/utils/is.js
function isObject(value) {
	return value !== null && typeof value === "object";
}
var CLASS_VALUE_PRIMITIVE_TYPES = [
	"string",
	"number",
	"bigint",
	"boolean"
];
function isClassValue(value) {
	if (value === null || value === void 0) return true;
	if (CLASS_VALUE_PRIMITIVE_TYPES.includes(typeof value)) return true;
	if (Array.isArray(value)) return value.every((item) => isClassValue(item));
	if (typeof value === "object") {
		if (Object.getPrototypeOf(value) !== Object.prototype) return false;
		return true;
	}
	return false;
}
//#endregion
//#region node_modules/svelte-toolbelt/dist/box/box-extras.svelte.js
var BoxSymbol = Symbol("box");
var isWritableSymbol = Symbol("is-writable");
function boxWith(getter, setter) {
	const derived$1 = derived(getter);
	if (setter) return {
		[BoxSymbol]: true,
		[isWritableSymbol]: true,
		get current() {
			return derived$1();
		},
		set current(v) {
			setter(v);
		}
	};
	return {
		[BoxSymbol]: true,
		get current() {
			return getter();
		}
	};
}
/**
* @returns Whether the value is a Box
*
* @see {@link https://runed.dev/docs/functions/box}
*/
function isBox(value) {
	return isObject(value) && BoxSymbol in value;
}
function simpleBox(initialValue) {
	let current = initialValue;
	return {
		[BoxSymbol]: true,
		[isWritableSymbol]: true,
		get current() {
			return current;
		},
		set current(v) {
			current = v;
		}
	};
}
//#endregion
//#region node_modules/svelte-toolbelt/dist/utils/compose-handlers.js
/**
* Composes event handlers into a single function that can be called with an event.
* If the previous handler cancels the event using `event.preventDefault()`, the handlers
* that follow will not be called.
*/
function composeHandlers(...handlers) {
	return function(e) {
		for (const handler of handlers) {
			if (!handler) continue;
			if (e.defaultPrevented) return;
			if (typeof handler === "function") handler.call(this, e);
			else handler.current?.call(this, e);
		}
	};
}
//#endregion
//#region node_modules/svelte-toolbelt/dist/utils/strings.js
var NUMBER_CHAR_RE = /\d/;
var STR_SPLITTERS = [
	"-",
	"_",
	"/",
	"."
];
function isUppercase(char = "") {
	if (NUMBER_CHAR_RE.test(char)) return void 0;
	return char !== char.toLowerCase();
}
function splitByCase(str) {
	const parts = [];
	let buff = "";
	let previousUpper;
	let previousSplitter;
	for (const char of str) {
		const isSplitter = STR_SPLITTERS.includes(char);
		if (isSplitter === true) {
			parts.push(buff);
			buff = "";
			previousUpper = void 0;
			continue;
		}
		const isUpper = isUppercase(char);
		if (previousSplitter === false) {
			if (previousUpper === false && isUpper === true) {
				parts.push(buff);
				buff = char;
				previousUpper = isUpper;
				continue;
			}
			if (previousUpper === true && isUpper === false && buff.length > 1) {
				const lastChar = buff.at(-1);
				parts.push(buff.slice(0, Math.max(0, buff.length - 1)));
				buff = lastChar + char;
				previousUpper = isUpper;
				continue;
			}
		}
		buff += char;
		previousUpper = isUpper;
		previousSplitter = isSplitter;
	}
	parts.push(buff);
	return parts;
}
function pascalCase(str) {
	if (!str) return "";
	return splitByCase(str).map((p) => upperFirst(p)).join("");
}
function camelCase(str) {
	return lowerFirst(pascalCase(str || ""));
}
function upperFirst(str) {
	return str ? str[0].toUpperCase() + str.slice(1) : "";
}
function lowerFirst(str) {
	return str ? str[0].toLowerCase() + str.slice(1) : "";
}
//#endregion
//#region node_modules/svelte-toolbelt/dist/utils/css-to-style-obj.js
function cssToStyleObj(css) {
	if (!css) return {};
	const styleObj = {};
	function iterator(name, value) {
		if (name.startsWith("-moz-") || name.startsWith("-webkit-") || name.startsWith("-ms-") || name.startsWith("-o-")) {
			styleObj[pascalCase(name)] = value;
			return;
		}
		if (name.startsWith("--")) {
			styleObj[name] = value;
			return;
		}
		styleObj[camelCase(name)] = value;
	}
	parse(css, iterator);
	return styleObj;
}
//#endregion
//#region node_modules/svelte-toolbelt/dist/utils/execute-callbacks.js
/**
* Executes an array of callback functions with the same arguments.
* @template T The types of the arguments that the callback functions take.
* @param callbacks array of callback functions to execute.
* @returns A new function that executes all of the original callback functions with the same arguments.
*/
function executeCallbacks(...callbacks) {
	return (...args) => {
		for (const callback of callbacks) if (typeof callback === "function") callback(...args);
	};
}
//#endregion
//#region node_modules/svelte-toolbelt/dist/utils/style-to-css.js
function createParser(matcher, replacer) {
	const regex = RegExp(matcher, "g");
	return (str) => {
		if (typeof str !== "string") throw new TypeError(`expected an argument of type string, but got ${typeof str}`);
		if (!str.match(regex)) return str;
		return str.replace(regex, replacer);
	};
}
var camelToKebab = createParser(/[A-Z]/, (match) => `-${match.toLowerCase()}`);
function styleToCSS(styleObj) {
	if (!styleObj || typeof styleObj !== "object" || Array.isArray(styleObj)) throw new TypeError(`expected an argument of type object, but got ${typeof styleObj}`);
	return Object.keys(styleObj).map((property) => `${camelToKebab(property)}: ${styleObj[property]};`).join("\n");
}
//#endregion
//#region node_modules/svelte-toolbelt/dist/utils/style.js
function styleToString(style = {}) {
	return styleToCSS(style).replace("\n", " ");
}
var EVENT_LIST_SET = /* @__PURE__ */ new Set([
	"onabort",
	"onanimationcancel",
	"onanimationend",
	"onanimationiteration",
	"onanimationstart",
	"onauxclick",
	"onbeforeinput",
	"onbeforetoggle",
	"onblur",
	"oncancel",
	"oncanplay",
	"oncanplaythrough",
	"onchange",
	"onclick",
	"onclose",
	"oncompositionend",
	"oncompositionstart",
	"oncompositionupdate",
	"oncontextlost",
	"oncontextmenu",
	"oncontextrestored",
	"oncopy",
	"oncuechange",
	"oncut",
	"ondblclick",
	"ondrag",
	"ondragend",
	"ondragenter",
	"ondragleave",
	"ondragover",
	"ondragstart",
	"ondrop",
	"ondurationchange",
	"onemptied",
	"onended",
	"onerror",
	"onfocus",
	"onfocusin",
	"onfocusout",
	"onformdata",
	"ongotpointercapture",
	"oninput",
	"oninvalid",
	"onkeydown",
	"onkeypress",
	"onkeyup",
	"onload",
	"onloadeddata",
	"onloadedmetadata",
	"onloadstart",
	"onlostpointercapture",
	"onmousedown",
	"onmouseenter",
	"onmouseleave",
	"onmousemove",
	"onmouseout",
	"onmouseover",
	"onmouseup",
	"onpaste",
	"onpause",
	"onplay",
	"onplaying",
	"onpointercancel",
	"onpointerdown",
	"onpointerenter",
	"onpointerleave",
	"onpointermove",
	"onpointerout",
	"onpointerover",
	"onpointerup",
	"onprogress",
	"onratechange",
	"onreset",
	"onresize",
	"onscroll",
	"onscrollend",
	"onsecuritypolicyviolation",
	"onseeked",
	"onseeking",
	"onselect",
	"onselectionchange",
	"onselectstart",
	"onslotchange",
	"onstalled",
	"onsubmit",
	"onsuspend",
	"ontimeupdate",
	"ontoggle",
	"ontouchcancel",
	"ontouchend",
	"ontouchmove",
	"ontouchstart",
	"ontransitioncancel",
	"ontransitionend",
	"ontransitionrun",
	"ontransitionstart",
	"onvolumechange",
	"onwaiting",
	"onwebkitanimationend",
	"onwebkitanimationiteration",
	"onwebkitanimationstart",
	"onwebkittransitionend",
	"onwheel"
]);
//#endregion
//#region node_modules/svelte-toolbelt/dist/utils/merge-props.js
/**
* Modified from https://github.com/adobe/react-spectrum/blob/main/packages/%40react-aria/utils/src/mergeProps.ts (see NOTICE.txt for source)
*/
function isEventHandler(key) {
	return EVENT_LIST_SET.has(key);
}
/**
* Given a list of prop objects, merges them into a single object.
* - Automatically composes event handlers (e.g. `onclick`, `oninput`, etc.)
* - Chains regular functions with the same name so they are called in order
* - Merges class strings with `clsx`
* - Merges style objects and converts them to strings
* - Handles a bug with Svelte where setting the `hidden` attribute to `false` doesn't remove it
* - Overrides other values with the last one
*/
function mergeProps(...args) {
	const result = { ...args[0] };
	for (let i = 1; i < args.length; i++) {
		const props = args[i];
		if (!props) continue;
		for (const key of Object.keys(props)) {
			const a = result[key];
			const b = props[key];
			const aIsFunction = typeof a === "function";
			const bIsFunction = typeof b === "function";
			if (aIsFunction && typeof bIsFunction && isEventHandler(key)) result[key] = composeHandlers(a, b);
			else if (aIsFunction && bIsFunction) result[key] = executeCallbacks(a, b);
			else if (key === "class") {
				const aIsClassValue = isClassValue(a);
				const bIsClassValue = isClassValue(b);
				if (aIsClassValue && bIsClassValue) result[key] = clsx(a, b);
				else if (aIsClassValue) result[key] = clsx(a);
				else if (bIsClassValue) result[key] = clsx(b);
			} else if (key === "style") {
				const aIsObject = typeof a === "object";
				const bIsObject = typeof b === "object";
				const aIsString = typeof a === "string";
				const bIsString = typeof b === "string";
				if (aIsObject && bIsObject) result[key] = {
					...a,
					...b
				};
				else if (aIsObject && bIsString) {
					const parsedStyle = cssToStyleObj(b);
					result[key] = {
						...a,
						...parsedStyle
					};
				} else if (aIsString && bIsObject) result[key] = {
					...cssToStyleObj(a),
					...b
				};
				else if (aIsString && bIsString) {
					const parsedStyleA = cssToStyleObj(a);
					const parsedStyleB = cssToStyleObj(b);
					result[key] = {
						...parsedStyleA,
						...parsedStyleB
					};
				} else if (aIsObject) result[key] = a;
				else if (bIsObject) result[key] = b;
				else if (aIsString) result[key] = a;
				else if (bIsString) result[key] = b;
			} else result[key] = b !== void 0 ? b : a;
		}
		for (const key of Object.getOwnPropertySymbols(props)) {
			const a = result[key];
			const b = props[key];
			result[key] = b !== void 0 ? b : a;
		}
	}
	if (typeof result.style === "object") result.style = styleToString(result.style).replaceAll("\n", " ");
	if (result.hidden === false) {
		result.hidden = void 0;
		delete result.hidden;
	}
	if (result.disabled === false) {
		result.disabled = void 0;
		delete result.disabled;
	}
	return result;
}
//#endregion
//#region node_modules/runed/dist/internal/configurable-globals.js
var defaultWindow = void 0;
//#endregion
//#region node_modules/runed/dist/internal/utils/dom.js
/**
* Handles getting the active element in a document or shadow root.
* If the active element is within a shadow root, it will traverse the shadow root
* to find the active element.
* If not, it will return the active element in the document.
*
* @param document A document or shadow root to get the active element from.
* @returns The active element in the document or shadow root.
*/
function getActiveElement$1(document) {
	let activeElement = document.activeElement;
	while (activeElement?.shadowRoot) {
		const node = activeElement.shadowRoot.activeElement;
		if (node === activeElement) break;
		else activeElement = node;
	}
	return activeElement;
}
//#endregion
//#region node_modules/runed/dist/utilities/active-element/active-element.svelte.js
var ActiveElement = class {
	#document;
	#subscribe;
	constructor(options = {}) {
		const { window = defaultWindow, document = window?.document } = options;
		if (window === void 0) return;
		this.#document = document;
		this.#subscribe = createSubscriber((update) => {
			const cleanupFocusIn = on(window, "focusin", update);
			const cleanupFocusOut = on(window, "focusout", update);
			return () => {
				cleanupFocusIn();
				cleanupFocusOut();
			};
		});
	}
	get current() {
		this.#subscribe?.();
		if (!this.#document) return null;
		return getActiveElement$1(this.#document);
	}
};
new ActiveElement();
//#endregion
//#region node_modules/runed/dist/utilities/context/context.js
var Context = class {
	#name;
	#key;
	/**
	* @param name The name of the context.
	* This is used for generating the context key and error messages.
	*/
	constructor(name) {
		this.#name = name;
		this.#key = Symbol(name);
	}
	/**
	* The key used to get and set the context.
	*
	* It is not recommended to use this value directly.
	* Instead, use the methods provided by this class.
	*/
	get key() {
		return this.#key;
	}
	/**
	* Checks whether this has been set in the context of a parent component.
	*
	* Must be called during component initialisation.
	*/
	exists() {
		return hasContext(this.#key);
	}
	/**
	* Retrieves the context that belongs to the closest parent component.
	*
	* Must be called during component initialisation.
	*
	* @throws An error if the context does not exist.
	*/
	get() {
		const context = getContext(this.#key);
		if (context === void 0) throw new Error(`Context "${this.#name}" not found`);
		return context;
	}
	/**
	* Retrieves the context that belongs to the closest parent component,
	* or the given fallback value if the context does not exist.
	*
	* Must be called during component initialisation.
	*/
	getOr(fallback) {
		const context = getContext(this.#key);
		if (context === void 0) return fallback;
		return context;
	}
	/**
	* Associates the given value with the current component and returns it.
	*
	* Must be called during component initialisation.
	*/
	set(context) {
		return setContext(this.#key, context);
	}
};
//#endregion
//#region node_modules/runed/dist/utilities/watch/watch.svelte.js
function runWatcher(sources, flush, effect, options = {}) {
	const { lazy = false } = options;
}
function watch(sources, effect, options) {
	runWatcher(sources, "post", effect, options);
}
function watchPre(sources, effect, options) {
	runWatcher(sources, "pre", effect, options);
}
watch.pre = watchPre;
function watchOnce(source, effect) {}
function watchOncePre(source, effect) {}
watchOnce.pre = watchOncePre;
//#endregion
//#region node_modules/runed/dist/utilities/resource/resource.svelte.js
function debounce$1(fn, delay) {
	let timeoutId;
	let lastResolve = null;
	return (...args) => {
		return new Promise((resolve) => {
			if (lastResolve) lastResolve(void 0);
			lastResolve = resolve;
			clearTimeout(timeoutId);
			timeoutId = setTimeout(async () => {
				const result = await fn(...args);
				if (lastResolve) {
					lastResolve(result);
					lastResolve = null;
				}
			}, delay);
		});
	};
}
function throttle(fn, delay) {
	let lastRun = 0;
	let lastPromise = null;
	return (...args) => {
		const now = Date.now();
		if (lastRun && now - lastRun < delay) return lastPromise ?? Promise.resolve(void 0);
		lastRun = now;
		lastPromise = fn(...args);
		return lastPromise;
	};
}
function runResource(source, fetcher, options = {}, effectFn) {
	const { lazy = false, once = false, initialValue, debounce: debounceTime, throttle: throttleTime } = options;
	let current = initialValue;
	let loading = false;
	let error = void 0;
	let cleanupFns = [];
	const runCleanup = () => {
		cleanupFns.forEach((fn) => fn());
		cleanupFns = [];
	};
	const onCleanup = (fn) => {
		cleanupFns = [...cleanupFns, fn];
	};
	const baseFetcher = async (value, previousValue, refetching = false) => {
		try {
			loading = true;
			error = void 0;
			runCleanup();
			const controller = new AbortController();
			onCleanup(() => controller.abort());
			const result = await fetcher(value, previousValue, {
				data: current,
				refetching,
				onCleanup,
				signal: controller.signal
			});
			current = result;
			return result;
		} catch (e) {
			if (!(e instanceof DOMException && e.name === "AbortError")) error = e;
			return;
		} finally {
			loading = false;
		}
	};
	const runFetcher = debounceTime ? debounce$1(baseFetcher, debounceTime) : throttleTime ? throttle(baseFetcher, throttleTime) : baseFetcher;
	const sources = Array.isArray(source) ? source : [source];
	let prevValues;
	effectFn((values, previousValues) => {
		if (once && prevValues) return;
		prevValues = values;
		runFetcher(Array.isArray(source) ? values : values[0], Array.isArray(source) ? previousValues : previousValues?.[0]);
	}, { lazy });
	return {
		get current() {
			return current;
		},
		get loading() {
			return loading;
		},
		get error() {
			return error;
		},
		mutate: (value) => {
			current = value;
		},
		refetch: (info) => {
			const values = sources.map((s) => s());
			return runFetcher(Array.isArray(source) ? values : values[0], Array.isArray(source) ? values : values[0], info ?? true);
		}
	};
}
function resource(source, fetcher, options) {
	return runResource(source, fetcher, options, (fn, options) => {
		const sources = Array.isArray(source) ? source : [source];
		const getters = () => sources.map((s) => s());
		watch(getters, (values, previousValues) => {
			fn(values, previousValues ?? []);
		}, options);
	});
}
function resourcePre(source, fetcher, options) {
	return runResource(source, fetcher, options, (fn, options) => {
		const sources = Array.isArray(source) ? source : [source];
		const getter = () => sources.map((s) => s());
		watch.pre(getter, (values, previousValues) => {
			fn(values, previousValues ?? []);
		}, options);
	});
}
resource.pre = resourcePre;
//#endregion
//#region node_modules/svelte-toolbelt/dist/utils/after-sleep.js
/**
* A utility function that executes a callback after a specified number of milliseconds.
*/
function afterSleep(ms, cb) {
	return setTimeout(cb, ms);
}
//#endregion
//#region node_modules/svelte-toolbelt/dist/utils/after-tick.js
function afterTick(fn) {
	(/* @__PURE__ */ tick()).then(fn);
}
//#endregion
//#region node_modules/svelte-toolbelt/dist/utils/dom.js
var ELEMENT_NODE = 1;
var DOCUMENT_NODE = 9;
var DOCUMENT_FRAGMENT_NODE = 11;
function isHTMLElement$1(node) {
	return isObject(node) && node.nodeType === ELEMENT_NODE && typeof node.nodeName === "string";
}
function isDocument(node) {
	return isObject(node) && node.nodeType === DOCUMENT_NODE;
}
function isWindow(node) {
	return isObject(node) && node.constructor?.name === "VisualViewport";
}
function isNode(node) {
	return isObject(node) && node.nodeType !== void 0;
}
function isShadowRoot(node) {
	return isNode(node) && node.nodeType === DOCUMENT_FRAGMENT_NODE && "host" in node;
}
function contains(parent, child) {
	if (!parent || !child) return false;
	if (!isHTMLElement$1(parent) || !isHTMLElement$1(child)) return false;
	const rootNode = child.getRootNode?.();
	if (parent === child) return true;
	if (parent.contains(child)) return true;
	if (rootNode && isShadowRoot(rootNode)) {
		let next = child;
		while (next) {
			if (parent === next) return true;
			next = next.parentNode || next.host;
		}
	}
	return false;
}
function getDocument(node) {
	if (isDocument(node)) return node;
	if (isWindow(node)) return node.document;
	return node?.ownerDocument ?? document;
}
function getActiveElement(rootNode) {
	let activeElement = rootNode.activeElement;
	while (activeElement?.shadowRoot) {
		const el = activeElement.shadowRoot.activeElement;
		if (el === activeElement) break;
		else activeElement = el;
	}
	return activeElement;
}
//#endregion
//#region node_modules/svelte-toolbelt/dist/utils/dom-context.svelte.js
var DOMContext = class {
	element;
	#root = derived(() => {
		if (!this.element.current) return document;
		return this.element.current.getRootNode() ?? document;
	});
	get root() {
		return this.#root();
	}
	set root($$value) {
		return this.#root($$value);
	}
	constructor(element) {
		if (typeof element === "function") this.element = boxWith(element);
		else this.element = element;
	}
	getDocument = () => {
		return getDocument(this.root);
	};
	getWindow = () => {
		return this.getDocument().defaultView ?? window;
	};
	getActiveElement = () => {
		return getActiveElement(this.root);
	};
	isActiveElement = (node) => {
		return node === this.getActiveElement();
	};
	getElementById(id) {
		return this.root.getElementById(id);
	}
	querySelector = (selector) => {
		if (!this.root) return null;
		return this.root.querySelector(selector);
	};
	querySelectorAll = (selector) => {
		if (!this.root) return [];
		return this.root.querySelectorAll(selector);
	};
	setTimeout = (callback, delay) => {
		return this.getWindow().setTimeout(callback, delay);
	};
	clearTimeout = (timeoutId) => {
		return this.getWindow().clearTimeout(timeoutId);
	};
};
if (typeof HTMLElement === "function");
//#endregion
//#region node_modules/svelte/src/attachments/index.js
/**
* Creates an object key that will be recognised as an attachment when the object is spread onto an element,
* as a programmatic alternative to using `{@attach ...}`. This can be useful for library authors, though
* is generally not needed when building an app.
*
* ```svelte
* <script>
* 	import { createAttachmentKey } from 'svelte/attachments';
*
* 	const props = {
* 		class: 'cool',
* 		onclick: () => alert('clicked'),
* 		[createAttachmentKey()]: (node) => {
* 			node.textContent = 'attached!';
* 		}
* 	};
* <\/script>
*
* <button {...props}>click me</button>
* ```
* @since 5.29
*/
function createAttachmentKey() {
	return Symbol(ATTACHMENT_KEY);
}
//#endregion
//#region node_modules/svelte-toolbelt/dist/utils/attach-ref.js
/**
* Creates a Svelte Attachment that attaches a DOM element to a ref.
* The ref can be either a WritableBox or a callback function.
*
* @param ref - Either a WritableBox to store the element in, or a callback function that receives the element
* @param onChange - Optional callback that fires when the ref changes
* @returns An object with a spreadable attachment key that should be spread onto the element
*
* @example
* // Using with WritableBox
* const ref = box<HTMLDivElement | null>(null);
* <div {...attachRef(ref)}>Content</div>
*
* @example
* // Using with callback
* <div {...attachRef((node) => myNode = node)}>Content</div>
*
* @example
* // Using with onChange
* <div {...attachRef(ref, (node) => console.log(node))}>Content</div>
*/
function attachRef(ref, onChange) {
	return { [createAttachmentKey()]: (node) => {
		if (isBox(ref)) {
			ref.current = node;
			run(() => onChange?.(node));
			return () => {
				if ("isConnected" in node && node.isConnected) return;
				ref.current = null;
				onChange?.(null);
			};
		}
		ref(node);
		run(() => onChange?.(node));
		return () => {
			if ("isConnected" in node && node.isConnected) return;
			ref(null);
			onChange?.(null);
		};
	} };
}
//#endregion
//#region node_modules/bits-ui/dist/internal/attrs.js
function boolToEmptyStrOrUndef(condition) {
	return condition ? "" : void 0;
}
function getDataOpenClosed(condition) {
	return condition ? "open" : "closed";
}
function getDataTransitionAttrs(state) {
	if (state === "starting") return { "data-starting-style": "" };
	if (state === "ending") return { "data-ending-style": "" };
	return {};
}
var BitsAttrs = class {
	#variant;
	#prefix;
	attrs;
	constructor(config) {
		this.#variant = config.getVariant ? config.getVariant() : null;
		this.#prefix = this.#variant ? `data-${this.#variant}-` : `data-${config.component}-`;
		this.getAttr = this.getAttr.bind(this);
		this.selector = this.selector.bind(this);
		this.attrs = Object.fromEntries(config.parts.map((part) => [part, this.getAttr(part)]));
	}
	getAttr(part, variantOverride) {
		if (variantOverride) return `data-${variantOverride}-${part}`;
		return `${this.#prefix}${part}`;
	}
	selector(part, variantOverride) {
		return `[${this.getAttr(part, variantOverride)}]`;
	}
};
function createBitsAttrs(config) {
	const bitsAttrs = new BitsAttrs(config);
	return {
		...bitsAttrs.attrs,
		selector: bitsAttrs.selector,
		getAttr: bitsAttrs.getAttr
	};
}
//#endregion
//#region node_modules/bits-ui/dist/internal/is.js
var isBrowser = typeof document !== "undefined";
var isIOS = getIsIOS();
function getIsIOS() {
	return isBrowser && window?.navigator?.userAgent && (/iP(ad|hone|od)/.test(window.navigator.userAgent) || window?.navigator?.maxTouchPoints > 2 && /iPad|Macintosh/.test(window?.navigator.userAgent));
}
function isHTMLElement(element) {
	return element instanceof HTMLElement;
}
function isElementOrSVGElement(element) {
	return element instanceof Element || element instanceof SVGElement;
}
//#endregion
//#region node_modules/bits-ui/dist/internal/animations-complete.js
var AnimationsComplete = class {
	#opts;
	#currentFrame = null;
	#observer = null;
	#runId = 0;
	constructor(opts) {
		this.#opts = opts;
	}
	#cleanup() {
		if (this.#currentFrame !== null) {
			window.cancelAnimationFrame(this.#currentFrame);
			this.#currentFrame = null;
		}
		this.#observer?.disconnect();
		this.#observer = null;
		this.#runId++;
	}
	run(fn) {
		this.#cleanup();
		const node = this.#opts.ref.current;
		if (!node) return;
		if (typeof node.getAnimations !== "function") {
			this.#executeCallback(fn);
			return;
		}
		const runId = this.#runId;
		const executeIfCurrent = () => {
			if (runId !== this.#runId) return;
			this.#executeCallback(fn);
		};
		const waitForAnimations = () => {
			if (runId !== this.#runId) return;
			const animations = node.getAnimations();
			if (animations.length === 0) {
				executeIfCurrent();
				return;
			}
			Promise.all(animations.map((animation) => animation.finished)).then(() => {
				executeIfCurrent();
			}).catch(() => {
				if (runId !== this.#runId) return;
				if (node.getAnimations().some((animation) => animation.pending || animation.playState !== "finished")) {
					waitForAnimations();
					return;
				}
				executeIfCurrent();
			});
		};
		const requestWaitForAnimations = () => {
			this.#currentFrame = window.requestAnimationFrame(() => {
				this.#currentFrame = null;
				waitForAnimations();
			});
		};
		if (!this.#opts.afterTick.current) {
			requestWaitForAnimations();
			return;
		}
		this.#currentFrame = window.requestAnimationFrame(() => {
			this.#currentFrame = null;
			const startingStyleAttr = "data-starting-style";
			if (!node.hasAttribute(startingStyleAttr)) {
				requestWaitForAnimations();
				return;
			}
			this.#observer = new MutationObserver(() => {
				if (runId !== this.#runId) return;
				if (node.hasAttribute(startingStyleAttr)) return;
				this.#observer?.disconnect();
				this.#observer = null;
				requestWaitForAnimations();
			});
			this.#observer.observe(node, {
				attributes: true,
				attributeFilter: [startingStyleAttr]
			});
		});
	}
	#executeCallback(fn) {
		const execute = () => {
			fn();
		};
		if (this.#opts.afterTick) afterTick(execute);
		else execute();
	}
};
//#endregion
//#region node_modules/bits-ui/dist/internal/presence-manager.svelte.js
var PresenceManager = class {
	#opts;
	#enabled;
	#afterAnimations;
	#shouldRender = false;
	#transitionStatus = void 0;
	#hasMounted = false;
	#transitionFrame = null;
	constructor(opts) {
		this.#opts = opts;
		this.#shouldRender = opts.open.current;
		this.#enabled = opts.enabled ?? true;
		this.#afterAnimations = new AnimationsComplete({
			ref: this.#opts.ref,
			afterTick: this.#opts.open
		});
		watch(() => this.#opts.open.current, (isOpen) => {
			if (!this.#hasMounted) {
				this.#hasMounted = true;
				return;
			}
			this.#clearTransitionFrame();
			if (!isOpen && this.#opts.shouldSkipExitAnimation?.()) {
				this.#shouldRender = false;
				this.#transitionStatus = void 0;
				this.#opts.onComplete?.();
				return;
			}
			if (isOpen) this.#shouldRender = true;
			this.#transitionStatus = isOpen ? "starting" : "ending";
			if (isOpen) this.#transitionFrame = window.requestAnimationFrame(() => {
				this.#transitionFrame = null;
				if (this.#opts.open.current) this.#transitionStatus = void 0;
			});
			if (!this.#enabled) {
				if (!isOpen) this.#shouldRender = false;
				this.#transitionStatus = void 0;
				this.#opts.onComplete?.();
				return;
			}
			this.#afterAnimations.run(() => {
				if (isOpen === this.#opts.open.current) {
					if (!this.#opts.open.current) this.#shouldRender = false;
					this.#transitionStatus = void 0;
					this.#opts.onComplete?.();
				}
			});
		});
	}
	get shouldRender() {
		return this.#shouldRender;
	}
	get transitionStatus() {
		return this.#transitionStatus;
	}
	#clearTransitionFrame() {
		if (this.#transitionFrame === null) return;
		window.cancelAnimationFrame(this.#transitionFrame);
		this.#transitionFrame = null;
	}
};
//#endregion
//#region node_modules/bits-ui/dist/internal/noop.js
/**
* A no operation function (does nothing)
*/
function noop$1() {}
//#endregion
//#region node_modules/bits-ui/dist/internal/create-id.js
function createId(prefixOrUid, uid) {
	if (uid === void 0) return `bits-${prefixOrUid}`;
	return `bits-${prefixOrUid}-${uid}`;
}
//#endregion
//#region node_modules/bits-ui/dist/bits/dialog/dialog.svelte.js
var dialogAttrs = createBitsAttrs({
	component: "dialog",
	parts: [
		"content",
		"trigger",
		"overlay",
		"title",
		"description",
		"close",
		"cancel",
		"action"
	]
});
var DialogRootContext = new Context("Dialog.Root | AlertDialog.Root");
var DialogRootState = class DialogRootState {
	static create(opts) {
		const parent = DialogRootContext.getOr(null);
		return DialogRootContext.set(new DialogRootState(opts, parent));
	}
	opts;
	triggerNode = null;
	contentNode = null;
	overlayNode = null;
	descriptionNode = null;
	contentId = void 0;
	titleId = void 0;
	triggerId = void 0;
	descriptionId = void 0;
	cancelNode = null;
	nestedOpenCount = 0;
	depth;
	parent;
	contentPresence;
	overlayPresence;
	constructor(opts, parent) {
		this.opts = opts;
		this.parent = parent;
		this.depth = parent ? parent.depth + 1 : 0;
		this.handleOpen = this.handleOpen.bind(this);
		this.handleClose = this.handleClose.bind(this);
		this.contentPresence = new PresenceManager({
			ref: boxWith(() => this.contentNode),
			open: this.opts.open,
			enabled: true,
			onComplete: () => {
				this.opts.onOpenChangeComplete.current(this.opts.open.current);
			}
		});
		this.overlayPresence = new PresenceManager({
			ref: boxWith(() => this.overlayNode),
			open: this.opts.open,
			enabled: true
		});
		watch(() => this.opts.open.current, (isOpen) => {
			if (!this.parent) return;
			if (isOpen) this.parent.incrementNested();
			else this.parent.decrementNested();
		}, { lazy: true });
	}
	handleOpen() {
		if (this.opts.open.current) return;
		this.opts.open.current = true;
	}
	handleClose() {
		if (!this.opts.open.current) return;
		this.opts.open.current = false;
	}
	getBitsAttr = (part) => {
		return dialogAttrs.getAttr(part, this.opts.variant.current);
	};
	incrementNested() {
		this.nestedOpenCount++;
		this.parent?.incrementNested();
	}
	decrementNested() {
		if (this.nestedOpenCount === 0) return;
		this.nestedOpenCount--;
		this.parent?.decrementNested();
	}
	#sharedProps = derived(() => ({ "data-state": getDataOpenClosed(this.opts.open.current) }));
	get sharedProps() {
		return this.#sharedProps();
	}
	set sharedProps($$value) {
		return this.#sharedProps($$value);
	}
};
var DialogContentState = class DialogContentState {
	static create(opts) {
		return new DialogContentState(opts, DialogRootContext.get());
	}
	opts;
	root;
	attachment;
	constructor(opts, root) {
		this.opts = opts;
		this.root = root;
		this.attachment = attachRef(this.opts.ref, (v) => {
			this.root.contentNode = v;
			this.root.contentId = v?.id;
		});
	}
	#snippetProps = derived(() => ({ open: this.root.opts.open.current }));
	get snippetProps() {
		return this.#snippetProps();
	}
	set snippetProps($$value) {
		return this.#snippetProps($$value);
	}
	#props = derived(() => ({
		id: this.opts.id.current,
		role: this.root.opts.variant.current === "alert-dialog" ? "alertdialog" : "dialog",
		"aria-modal": "true",
		"aria-describedby": this.root.descriptionId,
		"aria-labelledby": this.root.titleId,
		[this.root.getBitsAttr("content")]: "",
		style: {
			pointerEvents: "auto",
			outline: this.root.opts.variant.current === "alert-dialog" ? "none" : void 0,
			"--bits-dialog-depth": this.root.depth,
			"--bits-dialog-nested-count": this.root.nestedOpenCount,
			contain: "layout style"
		},
		tabindex: this.root.opts.variant.current === "alert-dialog" ? -1 : void 0,
		"data-nested-open": boolToEmptyStrOrUndef(this.root.nestedOpenCount > 0),
		"data-nested": boolToEmptyStrOrUndef(this.root.parent !== null),
		...getDataTransitionAttrs(this.root.contentPresence.transitionStatus),
		...this.root.sharedProps,
		...this.attachment
	}));
	get props() {
		return this.#props();
	}
	set props($$value) {
		return this.#props($$value);
	}
	get shouldRender() {
		return this.root.contentPresence.shouldRender;
	}
};
var DialogOverlayState = class DialogOverlayState {
	static create(opts) {
		return new DialogOverlayState(opts, DialogRootContext.get());
	}
	opts;
	root;
	attachment;
	constructor(opts, root) {
		this.opts = opts;
		this.root = root;
		this.attachment = attachRef(this.opts.ref, (v) => this.root.overlayNode = v);
	}
	#snippetProps = derived(() => ({ open: this.root.opts.open.current }));
	get snippetProps() {
		return this.#snippetProps();
	}
	set snippetProps($$value) {
		return this.#snippetProps($$value);
	}
	#props = derived(() => ({
		id: this.opts.id.current,
		[this.root.getBitsAttr("overlay")]: "",
		style: {
			pointerEvents: "auto",
			"--bits-dialog-depth": this.root.depth,
			"--bits-dialog-nested-count": this.root.nestedOpenCount
		},
		"data-nested-open": boolToEmptyStrOrUndef(this.root.nestedOpenCount > 0),
		"data-nested": boolToEmptyStrOrUndef(this.root.parent !== null),
		...getDataTransitionAttrs(this.root.overlayPresence.transitionStatus),
		...this.root.sharedProps,
		...this.attachment
	}));
	get props() {
		return this.#props();
	}
	set props($$value) {
		return this.#props($$value);
	}
	get shouldRender() {
		return this.root.overlayPresence.shouldRender;
	}
};
//#endregion
//#region node_modules/bits-ui/dist/bits/utilities/portal/portal-consumer.svelte
function Portal_consumer($$renderer, $$props) {
	const { children } = $$props;
	$$renderer.push(`<!---->`);
	children?.($$renderer);
	$$renderer.push(`<!---->`);
	$$renderer.push(`<!---->`);
}
//#endregion
//#region node_modules/bits-ui/dist/bits/utilities/config/bits-config.js
var BitsConfigContext = new Context("BitsConfig");
/**
* Gets the current Bits UI configuration state from the context.
*
* Returns a default configuration (where all values are `undefined`) if no configuration is found.
*/
function getBitsConfig() {
	const fallback = new BitsConfigState(null, {});
	return BitsConfigContext.getOr(fallback).opts;
}
/**
* Configuration state that inherits from parent configurations.
*
* @example
* Config resolution:
* ```
* Level 1: { defaultPortalTo: "#some-element", theme: "dark" }
* Level 2: { spacing: "large" } // inherits defaultPortalTo="#some-element", theme="dark"
* Level 3: { theme: "light" }   // inherits defaultPortalTo="#some-element", spacing="large", overrides theme="light"
* ```
*/
var BitsConfigState = class {
	opts;
	constructor(parent, opts) {
		const resolveConfigOption = createConfigResolver(parent, opts);
		this.opts = {
			defaultPortalTo: resolveConfigOption((config) => config.defaultPortalTo),
			defaultLocale: resolveConfigOption((config) => config.defaultLocale)
		};
	}
};
/**
* Returns a config resolver that resolves a given config option's value.
*
* The resolver creates reactive boxes that resolve config option values using this priority:
* 1. Current level's value (if defined)
* 2. Parent level's value (if defined and current is undefined)
* 3. `undefined` (if no value is found in either parent or child)
*
* @param parent - Parent configuration state (null if this is root level)
* @param currentOpts - Current level's configuration options
*
* @example
* ```typescript
* // Given this hierarchy:
* // Root: { defaultPortalTo: "#some-element" }
* // Child: { someOtherProp: "value" } // no defaultPortalTo specified
*
* const resolveConfigOption = createConfigResolver(parent, opts);
* const portalTo = resolveConfigOption(config => config.defaultPortalTo);
*
* // portalTo.current === "#some-element" (inherited from parent)
* // even when child didn't specify `defaultPortalTo`
* ```
*/
function createConfigResolver(parent, currentOpts) {
	return (getter) => {
		return boxWith(() => {
			const value = getter(currentOpts)?.current;
			if (value !== void 0) return value;
			if (parent === null) return void 0;
			return getter(parent.opts)?.current;
		});
	};
}
//#endregion
//#region node_modules/bits-ui/dist/bits/utilities/config/prop-resolvers.js
/**
* Creates a generic prop resolver that follows a standard priority chain:
* 1. The getter's prop value (if defined)
* 2. The config default value (if no getter prop value is defined)
* 3. The fallback value (if no config value found)
*/
function createPropResolver(configOption, fallback) {
	return (getProp) => {
		const config = getBitsConfig();
		return boxWith(() => {
			const propValue = getProp();
			if (propValue !== void 0) return propValue;
			const option = configOption(config).current;
			if (option !== void 0) return option;
			return fallback;
		});
	};
}
/**
* Resolves a portal's `to` value using the prop, the config default, or a fallback.
*
* Default value: `"body"`
*/
var resolvePortalToProp = createPropResolver((config) => config.defaultPortalTo, "body");
//#endregion
//#region node_modules/bits-ui/dist/bits/utilities/portal/portal.svelte
function Portal($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { to: toProp, children, disabled } = $$props;
		const to = resolvePortalToProp(() => toProp);
		const context = getAllContexts();
		let target = derived(getTarget);
		function getTarget() {
			if (!isBrowser || disabled) return null;
			let localTarget = null;
			if (typeof to.current === "string") localTarget = document.querySelector(to.current);
			else localTarget = to.current;
			return localTarget;
		}
		let instance;
		function unmountInstance() {
			if (instance) {
				unmount(instance);
				instance = null;
			}
		}
		watch([() => target(), () => disabled], ([target, disabled]) => {
			if (!target || disabled) {
				unmountInstance();
				return;
			}
			instance = mount(Portal_consumer, {
				target,
				props: { children },
				context
			});
			return () => {
				unmountInstance();
			};
		});
		if (disabled) {
			$$renderer.push("<!--[0-->");
			children?.($$renderer);
			$$renderer.push(`<!---->`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]-->`);
	});
}
//#endregion
//#region node_modules/bits-ui/dist/internal/events.js
/**
* Creates a typed event dispatcher and listener pair for custom events
* @template T - The type of data that will be passed in the event detail
* @param eventName - The name of the custom event
* @param options - CustomEvent options (bubbles, cancelable, etc.)
*/
var CustomEventDispatcher = class {
	eventName;
	options;
	constructor(eventName, options = {
		bubbles: true,
		cancelable: true
	}) {
		this.eventName = eventName;
		this.options = options;
	}
	createEvent(detail) {
		return new CustomEvent(this.eventName, {
			...this.options,
			detail
		});
	}
	dispatch(element, detail) {
		const event = this.createEvent(detail);
		element.dispatchEvent(event);
		return event;
	}
	listen(element, callback, options) {
		const handler = (event) => {
			callback(event);
		};
		return on(element, this.eventName, handler, options);
	}
};
//#endregion
//#region node_modules/bits-ui/dist/internal/debounce.js
function debounce(fn, wait = 500) {
	let timeout = null;
	const debounced = (...args) => {
		if (timeout !== null) clearTimeout(timeout);
		timeout = setTimeout(() => {
			fn(...args);
		}, wait);
	};
	debounced.destroy = () => {
		if (timeout !== null) {
			clearTimeout(timeout);
			timeout = null;
		}
	};
	return debounced;
}
//#endregion
//#region node_modules/bits-ui/dist/internal/elements.js
function isOrContainsTarget(node, target) {
	return node === target || node.contains(target);
}
function getOwnerDocument(el) {
	return el?.ownerDocument ?? document;
}
//#endregion
//#region node_modules/bits-ui/dist/internal/dom.js
/**
* Determines if the click event truly occurred outside the content node.
* This was added to handle password managers and other elements that may be injected
* into the DOM but visually appear inside the content.
*/
function isClickTrulyOutside(event, contentNode) {
	const { clientX, clientY } = event;
	const rect = contentNode.getBoundingClientRect();
	return clientX < rect.left || clientX > rect.right || clientY < rect.top || clientY > rect.bottom;
}
//#endregion
//#region node_modules/bits-ui/dist/bits/menu/menu.svelte.js
var CONTEXT_MENU_TRIGGER_ATTR = "data-context-menu-trigger";
var CONTEXT_MENU_CONTENT_ATTR = "data-context-menu-content";
new Context("Menu.Root");
new Context("Menu.Root | Menu.Sub");
new Context("Menu.Content");
new Context("Menu.Group | Menu.RadioGroup");
new Context("Menu.RadioGroup");
new Context("Menu.CheckboxGroup");
new CustomEventDispatcher("bitsmenuopen", {
	bubbles: false,
	cancelable: true
});
createBitsAttrs({
	component: "menu",
	parts: [
		"trigger",
		"content",
		"sub-trigger",
		"item",
		"group",
		"group-heading",
		"checkbox-group",
		"checkbox-item",
		"radio-group",
		"radio-item",
		"separator",
		"sub-content",
		"arrow"
	]
});
//#endregion
//#region node_modules/bits-ui/dist/bits/utilities/dismissible-layer/use-dismissable-layer.svelte.js
globalThis.bitsDismissableLayers ??= /* @__PURE__ */ new Map();
var DismissibleLayerState = class DismissibleLayerState {
	static create(opts) {
		return new DismissibleLayerState(opts);
	}
	opts;
	#interactOutsideProp;
	#behaviorType;
	#interceptedEvents = { pointerdown: false };
	#isResponsibleLayer = false;
	#isFocusInsideDOMTree = false;
	#documentObj = void 0;
	#onFocusOutside;
	#unsubClickListener = noop$1;
	constructor(opts) {
		this.opts = opts;
		this.#behaviorType = opts.interactOutsideBehavior;
		this.#interactOutsideProp = opts.onInteractOutside;
		this.#onFocusOutside = opts.onFocusOutside;
		let unsubEvents = noop$1;
		let pendingTimer = null;
		const clearPendingTimer = () => {
			if (pendingTimer != null) {
				clearTimeout(pendingTimer);
				pendingTimer = null;
			}
		};
		const cleanup = () => {
			clearPendingTimer();
			this.#resetState();
			globalThis.bitsDismissableLayers.delete(this);
			this.#handleInteractOutside.destroy();
			unsubEvents();
		};
		watch([() => this.opts.enabled.current, () => this.opts.ref.current], () => {
			if (!this.opts.enabled.current || !this.opts.ref.current) return;
			clearPendingTimer();
			pendingTimer = afterSleep(1, () => {
				pendingTimer = null;
				if (!this.opts.ref.current) return;
				globalThis.bitsDismissableLayers.set(this, this.#behaviorType);
				unsubEvents();
				unsubEvents = this.#addEventListeners();
			});
			return cleanup;
		});
	}
	#handleFocus = (event) => {
		if (event.defaultPrevented) return;
		if (!this.opts.ref.current) return;
		afterTick(() => {
			if (!this.opts.ref.current || this.#isTargetWithinLayer(event.target)) return;
			if (event.target && !this.#isFocusInsideDOMTree) this.#onFocusOutside.current?.(event);
		});
	};
	#addEventListeners() {
		return executeCallbacks(
			/**
			* CAPTURE INTERACTION START
			* mark interaction-start event as intercepted.
			* mark responsible layer during interaction start
			* to avoid checking if is responsible layer during interaction end
			* when a new floating element may have been opened.
			*/
			on(this.#documentObj, "pointerdown", executeCallbacks(this.#markInterceptedEvent, this.#markResponsibleLayer), { capture: true }),
			/**
			* BUBBLE INTERACTION START
			* Mark interaction-start event as non-intercepted. Debounce `onInteractOutsideStart`
			* to avoid prematurely checking if other events were intercepted.
			*/
			on(this.#documentObj, "pointerdown", executeCallbacks(this.#markNonInterceptedEvent, this.#handleInteractOutside)),
			/**
			* HANDLE FOCUS OUTSIDE
			*/
			on(this.#documentObj, "focusin", this.#handleFocus)
		);
	}
	#handleDismiss = (e) => {
		let event = e;
		if (event.defaultPrevented) event = createWrappedEvent(e);
		this.#interactOutsideProp.current(e);
	};
	#handleInteractOutside = debounce((e) => {
		if (!this.opts.ref.current) {
			this.#unsubClickListener();
			return;
		}
		const isEventValid = this.opts.isValidEvent.current(e, this.opts.ref.current) || isValidEvent(e, this.opts.ref.current);
		if (!this.#isResponsibleLayer || this.#isAnyEventIntercepted() || !isEventValid) {
			this.#unsubClickListener();
			return;
		}
		let event = e;
		if (event.defaultPrevented) event = createWrappedEvent(event);
		if (this.#behaviorType.current !== "close" && this.#behaviorType.current !== "defer-otherwise-close") {
			this.#unsubClickListener();
			return;
		}
		if (e.pointerType === "touch") {
			this.#unsubClickListener();
			this.#unsubClickListener = on(this.#documentObj, "click", this.#handleDismiss, { once: true });
		} else this.#interactOutsideProp.current(event);
	}, 10);
	#markInterceptedEvent = (e) => {
		this.#interceptedEvents[e.type] = true;
	};
	#markNonInterceptedEvent = (e) => {
		this.#interceptedEvents[e.type] = false;
	};
	#markResponsibleLayer = () => {
		if (!this.opts.ref.current) return;
		this.#isResponsibleLayer = isResponsibleLayer(this.opts.ref.current);
	};
	#isTargetWithinLayer = (target) => {
		if (!this.opts.ref.current) return false;
		return isOrContainsTarget(this.opts.ref.current, target);
	};
	#resetState = debounce(() => {
		for (const eventType in this.#interceptedEvents) this.#interceptedEvents[eventType] = false;
		this.#isResponsibleLayer = false;
	}, 20);
	#isAnyEventIntercepted() {
		return Object.values(this.#interceptedEvents).some(Boolean);
	}
	#onfocuscapture = () => {
		this.#isFocusInsideDOMTree = true;
	};
	#onblurcapture = () => {
		this.#isFocusInsideDOMTree = false;
	};
	props = {
		onfocuscapture: this.#onfocuscapture,
		onblurcapture: this.#onblurcapture
	};
};
function getTopMostDismissableLayer(layersArr = [...globalThis.bitsDismissableLayers]) {
	return layersArr.findLast(([_, { current: behaviorType }]) => behaviorType === "close" || behaviorType === "ignore");
}
function isResponsibleLayer(node) {
	const layersArr = [...globalThis.bitsDismissableLayers];
	/**
	* We first check if we can find a top layer with `close` or `ignore`.
	* If that top layer was found and matches the provided node, then the node is
	* responsible for the outside interaction. Otherwise, we know that all layers defer so
	* the first layer is the responsible one.
	*/
	const topMostLayer = getTopMostDismissableLayer(layersArr);
	if (topMostLayer) return topMostLayer[0].opts.ref.current === node;
	const [firstLayerNode] = layersArr[0];
	return firstLayerNode.opts.ref.current === node;
}
function isValidEvent(e, node) {
	const target = e.target;
	if (!isElementOrSVGElement(target)) return false;
	const targetIsContextMenuTrigger = Boolean(target.closest(`[${CONTEXT_MENU_TRIGGER_ATTR}]`));
	const nodeIsContextMenu = Boolean(node.closest(`[${CONTEXT_MENU_CONTENT_ATTR}]`));
	if ("button" in e && e.button > 0 && !targetIsContextMenuTrigger) return false;
	if ("button" in e && e.button === 0 && targetIsContextMenuTrigger && nodeIsContextMenu) return true;
	if (targetIsContextMenuTrigger && nodeIsContextMenu) return false;
	return getOwnerDocument(target).documentElement.contains(target) && !isOrContainsTarget(node, target) && isClickTrulyOutside(e, node);
}
function createWrappedEvent(e) {
	const capturedCurrentTarget = e.currentTarget;
	const capturedTarget = e.target;
	let newEvent;
	if (e instanceof PointerEvent) newEvent = new PointerEvent(e.type, e);
	else newEvent = new PointerEvent("pointerdown", e);
	let isPrevented = false;
	return new Proxy(newEvent, { get: (target, prop) => {
		if (prop === "currentTarget") return capturedCurrentTarget;
		if (prop === "target") return capturedTarget;
		if (prop === "preventDefault") return () => {
			isPrevented = true;
			if (typeof target.preventDefault === "function") target.preventDefault();
		};
		if (prop === "defaultPrevented") return isPrevented;
		if (prop in target) return target[prop];
		return e[prop];
	} });
}
//#endregion
//#region node_modules/bits-ui/dist/bits/utilities/dismissible-layer/dismissible-layer.svelte
function Dismissible_layer($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { interactOutsideBehavior = "close", onInteractOutside = noop$1, onFocusOutside = noop$1, id, children, enabled, isValidEvent = () => false, ref } = $$props;
		const dismissibleLayerState = DismissibleLayerState.create({
			id: boxWith(() => id),
			interactOutsideBehavior: boxWith(() => interactOutsideBehavior),
			onInteractOutside: boxWith(() => onInteractOutside),
			enabled: boxWith(() => enabled),
			onFocusOutside: boxWith(() => onFocusOutside),
			isValidEvent: boxWith(() => isValidEvent),
			ref
		});
		children?.($$renderer, { props: dismissibleLayerState.props });
		$$renderer.push(`<!---->`);
	});
}
//#endregion
//#region node_modules/bits-ui/dist/bits/utilities/escape-layer/use-escape-layer.svelte.js
globalThis.bitsEscapeLayers ??= /* @__PURE__ */ new Map();
var EscapeLayerState = class EscapeLayerState {
	static create(opts) {
		return new EscapeLayerState(opts);
	}
	opts;
	domContext;
	constructor(opts) {
		this.opts = opts;
		this.domContext = new DOMContext(this.opts.ref);
		let unsubEvents = noop$1;
		watch(() => opts.enabled.current, (enabled) => {
			if (enabled) {
				globalThis.bitsEscapeLayers.set(this, opts.escapeKeydownBehavior);
				unsubEvents = this.#addEventListener();
			}
			return () => {
				unsubEvents();
				globalThis.bitsEscapeLayers.delete(this);
			};
		});
	}
	#addEventListener = () => {
		return on(this.domContext.getDocument(), "keydown", this.#onkeydown, { passive: false });
	};
	#onkeydown = (e) => {
		if (e.key !== "Escape" || !isResponsibleEscapeLayer(this)) return;
		const clonedEvent = new KeyboardEvent(e.type, e);
		e.preventDefault();
		const behaviorType = this.opts.escapeKeydownBehavior.current;
		if (behaviorType !== "close" && behaviorType !== "defer-otherwise-close") return;
		this.opts.onEscapeKeydown.current(clonedEvent);
	};
};
function isResponsibleEscapeLayer(instance) {
	const layersArr = [...globalThis.bitsEscapeLayers];
	/**
	* We first check if we can find a top layer with `close` or `ignore`.
	* If that top layer was found and matches the provided node, then the node is
	* responsible for the escape. Otherwise, we know that all layers defer so
	* the first layer is the responsible one.
	*/
	const topMostLayer = layersArr.findLast(([_, { current: behaviorType }]) => behaviorType === "close" || behaviorType === "ignore");
	if (topMostLayer) return topMostLayer[0] === instance;
	const [firstLayerNode] = layersArr[0];
	return firstLayerNode === instance;
}
//#endregion
//#region node_modules/bits-ui/dist/bits/utilities/escape-layer/escape-layer.svelte
function Escape_layer($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { escapeKeydownBehavior = "close", onEscapeKeydown = noop$1, children, enabled, ref } = $$props;
		EscapeLayerState.create({
			escapeKeydownBehavior: boxWith(() => escapeKeydownBehavior),
			onEscapeKeydown: boxWith(() => onEscapeKeydown),
			enabled: boxWith(() => enabled),
			ref
		});
		children?.($$renderer);
		$$renderer.push(`<!---->`);
	});
}
//#endregion
//#region node_modules/bits-ui/dist/bits/utilities/focus-scope/focus-scope-manager.js
var FocusScopeManager = class FocusScopeManager {
	static instance;
	#scopeStack = simpleBox([]);
	#focusHistory = /* @__PURE__ */ new WeakMap();
	#preFocusHistory = /* @__PURE__ */ new WeakMap();
	static getInstance() {
		if (!this.instance) this.instance = new FocusScopeManager();
		return this.instance;
	}
	register(scope) {
		const current = this.getActive();
		if (current && current !== scope) current.pause();
		const activeElement = document.activeElement;
		if (activeElement && activeElement !== document.body) this.#preFocusHistory.set(scope, activeElement);
		this.#scopeStack.current = this.#scopeStack.current.filter((s) => s !== scope);
		this.#scopeStack.current.unshift(scope);
	}
	unregister(scope) {
		this.#scopeStack.current = this.#scopeStack.current.filter((s) => s !== scope);
		const next = this.getActive();
		if (next) next.resume();
	}
	getActive() {
		return this.#scopeStack.current[0];
	}
	setFocusMemory(scope, element) {
		this.#focusHistory.set(scope, element);
	}
	getFocusMemory(scope) {
		return this.#focusHistory.get(scope);
	}
	isActiveScope(scope) {
		return this.getActive() === scope;
	}
	setPreFocusMemory(scope, element) {
		this.#preFocusHistory.set(scope, element);
	}
	getPreFocusMemory(scope) {
		return this.#preFocusHistory.get(scope);
	}
	clearPreFocusMemory(scope) {
		this.#preFocusHistory.delete(scope);
	}
};
//#endregion
//#region node_modules/bits-ui/dist/bits/utilities/focus-scope/focus-scope.svelte.js
var FocusScope = class FocusScope {
	#paused = false;
	#container = null;
	#manager = FocusScopeManager.getInstance();
	#cleanupFns = [];
	#opts;
	constructor(opts) {
		this.#opts = opts;
	}
	get paused() {
		return this.#paused;
	}
	pause() {
		this.#paused = true;
	}
	resume() {
		this.#paused = false;
	}
	#cleanup() {
		for (const fn of this.#cleanupFns) fn();
		this.#cleanupFns = [];
	}
	mount(container) {
		if (this.#container) this.unmount();
		this.#container = container;
		this.#manager.register(this);
		this.#setupEventListeners();
		this.#handleOpenAutoFocus();
	}
	unmount() {
		if (!this.#container) return;
		this.#cleanup();
		this.#handleCloseAutoFocus();
		this.#manager.unregister(this);
		this.#manager.clearPreFocusMemory(this);
		this.#container = null;
	}
	#handleOpenAutoFocus() {
		if (!this.#container) return;
		const event = new CustomEvent("focusScope.onOpenAutoFocus", {
			bubbles: false,
			cancelable: true
		});
		this.#opts.onOpenAutoFocus.current(event);
		if (!event.defaultPrevented) requestAnimationFrame(() => {
			if (!this.#container) return;
			const firstTabbable = this.#getFirstTabbable();
			if (firstTabbable) {
				firstTabbable.focus();
				this.#manager.setFocusMemory(this, firstTabbable);
			} else this.#container.focus();
		});
	}
	#handleCloseAutoFocus() {
		const event = new CustomEvent("focusScope.onCloseAutoFocus", {
			bubbles: false,
			cancelable: true
		});
		this.#opts.onCloseAutoFocus.current?.(event);
		if (!event.defaultPrevented) {
			const preFocusedElement = this.#manager.getPreFocusMemory(this);
			if (preFocusedElement && document.contains(preFocusedElement)) try {
				preFocusedElement.focus();
			} catch {
				document.body.focus();
			}
		}
	}
	#setupEventListeners() {
		if (!this.#container || !this.#opts.trap.current) return;
		const container = this.#container;
		const doc = container.ownerDocument;
		const handleFocus = (e) => {
			if (this.#paused || !this.#manager.isActiveScope(this)) return;
			const target = e.target;
			if (!target) return;
			if (container.contains(target)) this.#manager.setFocusMemory(this, target);
			else {
				const lastFocused = this.#manager.getFocusMemory(this);
				if (lastFocused && container.contains(lastFocused) && isFocusable(lastFocused)) {
					e.preventDefault();
					lastFocused.focus();
				} else {
					const firstTabbable = this.#getFirstTabbable();
					const firstFocusable = this.#getAllFocusables()[0];
					(firstTabbable || firstFocusable || container).focus();
				}
			}
		};
		const handleKeydown = (e) => {
			if (!this.#opts.loop || this.#paused || e.key !== "Tab") return;
			if (!this.#manager.isActiveScope(this)) return;
			const tabbables = this.#getTabbables();
			if (tabbables.length === 0) return;
			const first = tabbables[0];
			const last = tabbables[tabbables.length - 1];
			if (!e.shiftKey && doc.activeElement === last) {
				e.preventDefault();
				first.focus();
			} else if (e.shiftKey && doc.activeElement === first) {
				e.preventDefault();
				last.focus();
			}
		};
		this.#cleanupFns.push(on(doc, "focusin", handleFocus, { capture: true }), on(container, "keydown", handleKeydown));
		const observer = new MutationObserver(() => {
			const lastFocused = this.#manager.getFocusMemory(this);
			if (lastFocused && !container.contains(lastFocused)) {
				const firstTabbable = this.#getFirstTabbable();
				const firstFocusable = this.#getAllFocusables()[0];
				const elementToFocus = firstTabbable || firstFocusable;
				if (elementToFocus) {
					elementToFocus.focus();
					this.#manager.setFocusMemory(this, elementToFocus);
				} else container.focus();
			}
		});
		observer.observe(container, {
			childList: true,
			subtree: true
		});
		this.#cleanupFns.push(() => observer.disconnect());
	}
	#getTabbables() {
		if (!this.#container) return [];
		return tabbable(this.#container, {
			includeContainer: false,
			getShadowRoot: true
		});
	}
	#getFirstTabbable() {
		return this.#getTabbables()[0] || null;
	}
	#getAllFocusables() {
		if (!this.#container) return [];
		return focusable(this.#container, {
			includeContainer: false,
			getShadowRoot: true
		});
	}
	static use(opts) {
		let scope = null;
		watch([() => opts.ref.current, () => opts.enabled.current], ([ref, enabled]) => {
			if (ref && enabled) {
				if (!scope) scope = new FocusScope(opts);
				scope.mount(ref);
			} else if (scope) {
				scope.unmount();
				scope = null;
			}
		});
		return { get props() {
			return { tabindex: -1 };
		} };
	}
};
//#endregion
//#region node_modules/bits-ui/dist/bits/utilities/focus-scope/focus-scope.svelte
function Focus_scope($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { enabled = false, trapFocus = false, loop = false, onCloseAutoFocus = noop$1, onOpenAutoFocus = noop$1, focusScope, ref } = $$props;
		const focusScopeState = FocusScope.use({
			enabled: boxWith(() => enabled),
			trap: boxWith(() => trapFocus),
			loop,
			onCloseAutoFocus: boxWith(() => onCloseAutoFocus),
			onOpenAutoFocus: boxWith(() => onOpenAutoFocus),
			ref
		});
		focusScope?.($$renderer, { props: focusScopeState.props });
		$$renderer.push(`<!---->`);
	});
}
//#endregion
//#region node_modules/bits-ui/dist/bits/utilities/text-selection-layer/use-text-selection-layer.svelte.js
var noopPointer = () => {};
globalThis.bitsTextSelectionLayers ??= /* @__PURE__ */ new Map();
var TextSelectionLayerState = class TextSelectionLayerState {
	static create(opts) {
		return new TextSelectionLayerState(opts);
	}
	opts;
	domContext;
	#unsubSelectionLock = noop$1;
	#enabledSnapshot = false;
	#onPointerDownSnapshot = noopPointer;
	#onPointerUpSnapshot = noopPointer;
	constructor(opts) {
		this.opts = opts;
		this.domContext = new DOMContext(opts.ref);
		let unsubEvents = noop$1;
		watch(() => [
			this.opts.enabled.current,
			this.opts.onPointerDown.current,
			this.opts.onPointerUp.current
		], ([enabled, onPointerDown, onPointerUp]) => {
			this.#enabledSnapshot = enabled;
			this.#onPointerDownSnapshot = onPointerDown;
			this.#onPointerUpSnapshot = onPointerUp;
			if (enabled) {
				globalThis.bitsTextSelectionLayers.set(this, this.opts.enabled);
				unsubEvents();
				unsubEvents = this.#addEventListeners();
			}
			return () => {
				this.#enabledSnapshot = false;
				unsubEvents();
				this.#resetSelectionLock();
				globalThis.bitsTextSelectionLayers.delete(this);
			};
		});
	}
	#addEventListeners() {
		return executeCallbacks(on(this.domContext.getDocument(), "pointerdown", this.#pointerdown), on(this.domContext.getDocument(), "pointerup", composeHandlers(this.#resetSelectionLock, this.#pointerupUserHandler)));
	}
	#pointerupUserHandler = (e) => {
		this.#onPointerUpSnapshot(e);
	};
	#pointerdown = (e) => {
		if (!this.#enabledSnapshot) return;
		const node = this.opts.ref.current;
		const target = e.target;
		if (!isHTMLElement(node) || !isHTMLElement(target)) return;
		/**
		* We only lock user-selection overflow if layer is the top most layer and
		* pointerdown occurred inside the node. You are still allowed to select text
		* outside the node provided pointerdown occurs outside the node.
		*/
		if (!isHighestLayer(this) || !contains(node, target)) return;
		this.#onPointerDownSnapshot(e);
		if (e.defaultPrevented) return;
		this.#unsubSelectionLock = preventTextSelectionOverflow(node, this.domContext.getDocument().body);
	};
	#resetSelectionLock = () => {
		this.#unsubSelectionLock();
		this.#unsubSelectionLock = noop$1;
	};
};
var getUserSelect = (node) => node.style.userSelect || node.style.webkitUserSelect;
function preventTextSelectionOverflow(node, body) {
	const originalBodyUserSelect = getUserSelect(body);
	const originalNodeUserSelect = getUserSelect(node);
	setUserSelect(body, "none");
	setUserSelect(node, "text");
	return () => {
		setUserSelect(body, originalBodyUserSelect);
		setUserSelect(node, originalNodeUserSelect);
	};
}
function setUserSelect(node, value) {
	node.style.userSelect = value;
	node.style.webkitUserSelect = value;
}
function isHighestLayer(instance) {
	const layersArr = [...globalThis.bitsTextSelectionLayers];
	if (!layersArr.length) return false;
	const highestLayer = layersArr.at(-1);
	if (!highestLayer) return false;
	return highestLayer[0] === instance;
}
//#endregion
//#region node_modules/bits-ui/dist/bits/utilities/text-selection-layer/text-selection-layer.svelte
function Text_selection_layer($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { preventOverflowTextSelection = true, onPointerDown = noop$1, onPointerUp = noop$1, id, children, enabled, ref } = $$props;
		TextSelectionLayerState.create({
			id: boxWith(() => id),
			onPointerDown: boxWith(() => onPointerDown),
			onPointerUp: boxWith(() => onPointerUp),
			enabled: boxWith(() => enabled && preventOverflowTextSelection),
			ref
		});
		children?.($$renderer);
		$$renderer.push(`<!---->`);
	});
}
//#endregion
//#region node_modules/bits-ui/dist/internal/use-id.js
globalThis.bitsIdCounter ??= { current: 0 };
/**
* Generates a unique ID based on a global counter.
*/
function useId(prefix = "bits") {
	globalThis.bitsIdCounter.current++;
	return `${prefix}-${globalThis.bitsIdCounter.current}`;
}
//#endregion
//#region node_modules/bits-ui/dist/internal/shared-state.svelte.js
var SharedState = class {
	#factory;
	#subscribers = 0;
	#state;
	#scope;
	constructor(factory) {
		this.#factory = factory;
	}
	#dispose() {
		this.#subscribers -= 1;
		if (this.#scope && this.#subscribers <= 0) {
			this.#scope();
			this.#state = void 0;
			this.#scope = void 0;
		}
	}
	get(...args) {
		this.#subscribers += 1;
		if (this.#state === void 0) this.#scope = () => {};
		return this.#state;
	}
};
//#endregion
//#region node_modules/bits-ui/dist/internal/body-scroll-lock.svelte.js
var lockMap = new SvelteMap();
var initialBodyStyle = null;
var cleanupTimeoutId = null;
var isInCleanupTransition = false;
var anyLocked = boxWith(() => {
	for (const value of lockMap.values()) if (value) return true;
	return false;
});
/**
* We track the time we scheduled the cleanup to prevent race conditions
* when multiple locks are created/destroyed in the same tick, ensuring
* only the last one to schedule the cleanup will run.
*
* reference: https://github.com/huntabyte/bits-ui/issues/1639
*/
var cleanupScheduledAt = null;
var bodyLockStackCount = new SharedState(() => {
	function resetBodyStyle() {}
	function cancelPendingCleanup() {
		if (cleanupTimeoutId === null) return;
		window.clearTimeout(cleanupTimeoutId);
		cleanupTimeoutId = null;
	}
	function scheduleCleanupIfNoNewLocks(delay, callback) {
		cancelPendingCleanup();
		isInCleanupTransition = true;
		cleanupScheduledAt = Date.now();
		const currentCleanupId = cleanupScheduledAt;
		/**
		* We schedule the cleanup to run after a delay to allow new locks to register
		* that might have been added in the same tick as the current cleanup.
		*
		* If a new lock is added in the same tick, the cleanup will be cancelled and
		* a new cleanup will be scheduled.
		*
		* This is to prevent the cleanup from running too early and resetting the body
		* style before the new lock has had a chance to apply its styles.
		*/
		const cleanupFn = () => {
			cleanupTimeoutId = null;
			if (cleanupScheduledAt !== currentCleanupId) return;
			if (!isAnyLocked(lockMap)) {
				isInCleanupTransition = false;
				callback();
			} else isInCleanupTransition = false;
		};
		const actualDelay = delay === null ? 24 : delay;
		cleanupTimeoutId = window.setTimeout(cleanupFn, actualDelay);
	}
	function ensureInitialStyleCaptured() {
		if (initialBodyStyle === null && lockMap.size === 0 && !isInCleanupTransition) initialBodyStyle = document.body.getAttribute("style");
	}
	watch(() => anyLocked.current, () => {
		if (!anyLocked.current) return;
		ensureInitialStyleCaptured();
		isInCleanupTransition = false;
		const htmlStyle = getComputedStyle(document.documentElement);
		const bodyStyle = getComputedStyle(document.body);
		const hasStableGutter = htmlStyle.scrollbarGutter?.includes("stable") || bodyStyle.scrollbarGutter?.includes("stable");
		const verticalScrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
		const config = {
			padding: Number.parseInt(bodyStyle.paddingRight ?? "0", 10) + verticalScrollbarWidth,
			margin: Number.parseInt(bodyStyle.marginRight ?? "0", 10)
		};
		if (verticalScrollbarWidth > 0 && !hasStableGutter) {
			document.body.style.paddingRight = `${config.padding}px`;
			document.body.style.marginRight = `${config.margin}px`;
			document.body.style.setProperty("--scrollbar-width", `${verticalScrollbarWidth}px`);
		}
		document.body.style.overflow = "hidden";
		if (isIOS) on(document, "touchmove", (e) => {
			if (e.target !== document.documentElement) return;
			if (e.touches.length > 1) return;
			e.preventDefault();
		}, { passive: false });
		/**
		* We ensure pointer-events: none is applied _after_ DOM updates, so that any focus/
		* interaction changes from opening overlays/menus complete _before_ we block pointer
		* events.
		*
		* this avoids race conditions where pointer-events could be set too early and break
		* focus/interaction.
		*/
		afterTick(() => {
			document.body.style.pointerEvents = "none";
			document.body.style.overflow = "hidden";
		});
	});
	return {
		get lockMap() {
			return lockMap;
		},
		resetBodyStyle,
		scheduleCleanupIfNoNewLocks,
		cancelPendingCleanup,
		ensureInitialStyleCaptured
	};
});
var BodyScrollLock = class {
	#id = useId();
	#initialState;
	#restoreScrollDelay = () => null;
	#countState;
	locked;
	constructor(initialState, restoreScrollDelay = () => null) {
		this.#initialState = initialState;
		this.#restoreScrollDelay = restoreScrollDelay;
		this.#countState = bodyLockStackCount.get();
		if (!this.#countState) return;
		/**
		* Since a new lock is being created, we cancel any pending cleanup to
		* prevent the cleanup from running too early and resetting the body style
		* before the new lock has had a chance to apply its styles.
		*
		* reference: https://github.com/huntabyte/bits-ui/issues/1639
		*/
		this.#countState.cancelPendingCleanup();
		this.#countState.ensureInitialStyleCaptured();
		this.#countState.lockMap.set(this.#id, this.#initialState ?? false);
		this.locked = boxWith(() => this.#countState.lockMap.get(this.#id) ?? false, (v) => this.#countState.lockMap.set(this.#id, v));
	}
};
function isAnyLocked(map) {
	for (const [_, value] of map) if (value) return true;
	return false;
}
//#endregion
//#region node_modules/bits-ui/dist/bits/utilities/scroll-lock/scroll-lock.svelte
function Scroll_lock($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { preventScroll = true, restoreScrollDelay = null } = $$props;
		if (preventScroll) new BodyScrollLock(preventScroll, () => restoreScrollDelay);
	});
}
//#endregion
//#region node_modules/bits-ui/dist/bits/dialog/components/dialog-overlay.svelte
function Dialog_overlay($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		const uid = props_id($$renderer);
		let { id = createId(uid), forceMount = false, child, children, ref = null, $$slots, $$events, ...restProps } = $$props;
		const overlayState = DialogOverlayState.create({
			id: boxWith(() => id),
			ref: boxWith(() => ref, (v) => ref = v)
		});
		const mergedProps = derived(() => mergeProps(restProps, overlayState.props));
		if (overlayState.shouldRender || forceMount) {
			$$renderer.push("<!--[0-->");
			if (child) {
				$$renderer.push("<!--[0-->");
				child($$renderer, {
					props: mergeProps(mergedProps()),
					...overlayState.snippetProps
				});
				$$renderer.push(`<!---->`);
			} else {
				$$renderer.push("<!--[-1-->");
				$$renderer.push(`<div${attributes({ ...mergeProps(mergedProps()) })}>`);
				children?.($$renderer, overlayState.snippetProps);
				$$renderer.push(`<!----></div>`);
			}
			$$renderer.push(`<!--]-->`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]-->`);
		bind_props($$props, { ref });
	});
}
//#endregion
//#region node_modules/bits-ui/dist/bits/dialog/components/dialog.svelte
function Dialog($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { open = false, onOpenChange = noop$1, onOpenChangeComplete = noop$1, children } = $$props;
		DialogRootState.create({
			variant: boxWith(() => "dialog"),
			open: boxWith(() => open, (v) => {
				open = v;
				onOpenChange(v);
			}),
			onOpenChangeComplete: boxWith(() => onOpenChangeComplete)
		});
		children?.($$renderer);
		$$renderer.push(`<!---->`);
		bind_props($$props, { open });
	});
}
//#endregion
//#region node_modules/bits-ui/dist/bits/dialog/components/dialog-content.svelte
function Dialog_content($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		const uid = props_id($$renderer);
		let { id = createId(uid), children, child, ref = null, forceMount = false, onCloseAutoFocus = noop$1, onOpenAutoFocus = noop$1, onEscapeKeydown = noop$1, onInteractOutside = noop$1, trapFocus = true, preventScroll = true, restoreScrollDelay = null, $$slots, $$events, ...restProps } = $$props;
		const contentState = DialogContentState.create({
			id: boxWith(() => id),
			ref: boxWith(() => ref, (v) => ref = v)
		});
		const mergedProps = derived(() => mergeProps(restProps, contentState.props));
		if (contentState.shouldRender || forceMount) {
			$$renderer.push("<!--[0-->");
			{
				function focusScope($$renderer, { props: focusScopeProps }) {
					Escape_layer($$renderer, spread_props([mergedProps(), {
						enabled: contentState.root.opts.open.current,
						ref: contentState.opts.ref,
						onEscapeKeydown: (e) => {
							onEscapeKeydown(e);
							if (e.defaultPrevented) return;
							contentState.root.handleClose();
						},
						children: ($$renderer) => {
							Dismissible_layer($$renderer, spread_props([mergedProps(), {
								ref: contentState.opts.ref,
								enabled: contentState.root.opts.open.current,
								onInteractOutside: (e) => {
									onInteractOutside(e);
									if (e.defaultPrevented) return;
									contentState.root.handleClose();
								},
								children: ($$renderer) => {
									Text_selection_layer($$renderer, spread_props([mergedProps(), {
										ref: contentState.opts.ref,
										enabled: contentState.root.opts.open.current,
										children: ($$renderer) => {
											if (child) {
												$$renderer.push("<!--[0-->");
												if (contentState.root.opts.open.current) {
													$$renderer.push("<!--[0-->");
													Scroll_lock($$renderer, {
														preventScroll,
														restoreScrollDelay
													});
												} else $$renderer.push("<!--[-1-->");
												$$renderer.push(`<!--]--> `);
												child($$renderer, {
													props: mergeProps(mergedProps(), focusScopeProps),
													...contentState.snippetProps
												});
												$$renderer.push(`<!---->`);
											} else {
												$$renderer.push("<!--[-1-->");
												Scroll_lock($$renderer, { preventScroll });
												$$renderer.push(`<!----> <div${attributes({ ...mergeProps(mergedProps(), focusScopeProps) })}>`);
												children?.($$renderer);
												$$renderer.push(`<!----></div>`);
											}
											$$renderer.push(`<!--]-->`);
										},
										$$slots: { default: true }
									}]));
								},
								$$slots: { default: true }
							}]));
						},
						$$slots: { default: true }
					}]));
				}
				Focus_scope($$renderer, {
					ref: contentState.opts.ref,
					loop: true,
					trapFocus,
					enabled: contentState.root.opts.open.current,
					onOpenAutoFocus,
					onCloseAutoFocus,
					focusScope,
					$$slots: { focusScope: true }
				});
			}
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]-->`);
		bind_props($$props, { ref });
	});
}
//#endregion
export { createMutation as a, Portal as i, Dialog as n, Dialog_overlay as r, Dialog_content as t };
