{
					__sveltekit_1pxkydu = {
						base: ""
					};

					const element = document.currentScript.parentElement;

					Promise.all([
						import("/_app/immutable/entry/start.CGIVEfEr.js"),
						import("/_app/immutable/entry/app.BK39b0he.js")
					]).then(([kit, app]) => {
						kit.start(app, element);
					});
				}
