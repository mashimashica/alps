export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set(["assets/icon.svg"]),
	mimeTypes: {".svg":"image/svg+xml"},
	_: {
		client: {start:"_app/immutable/entry/start.DDPDiTe1.js",app:"_app/immutable/entry/app._kzc2D2u.js",imports:["_app/immutable/entry/start.DDPDiTe1.js","_app/immutable/chunks/ze5M53Mr.js","_app/immutable/chunks/BpflPqBH.js","_app/immutable/entry/app._kzc2D2u.js","_app/immutable/chunks/BpflPqBH.js","_app/immutable/chunks/xihTtKlq.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js')),
			__memo(() => import('./nodes/2.js')),
			__memo(() => import('./nodes/3.js')),
			__memo(() => import('./nodes/4.js')),
			__memo(() => import('./nodes/5.js')),
			__memo(() => import('./nodes/6.js'))
		],
		remotes: {
			
		},
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 2 },
				endpoint: null
			},
			{
				id: "/analysis",
				pattern: /^\/analysis\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 3 },
				endpoint: null
			},
			{
				id: "/atlas",
				pattern: /^\/atlas\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 4 },
				endpoint: null
			},
			{
				id: "/library",
				pattern: /^\/library\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 5 },
				endpoint: null
			},
			{
				id: "/runs",
				pattern: /^\/runs\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 6 },
				endpoint: null
			}
		],
		prerendered_routes: new Set([]),
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();
