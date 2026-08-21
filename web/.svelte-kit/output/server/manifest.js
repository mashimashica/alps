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
			__memo(() => import('./nodes/1.js'))
		],
		remotes: {
			
		},
		routes: [
			
		],
		prerendered_routes: new Set(["/","/analysis","/atlas","/library","/runs"]),
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();
