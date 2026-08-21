{
					__sveltekit_4z0mk7 = {
						base: ""
					};

					const element = document.currentScript.parentElement;

					Promise.all([
						import("/_app/immutable/entry/start.Oy4Pf3Xn.js"),
						import("/_app/immutable/entry/app.B4pKdGZg.js")
					]).then(([kit, app]) => {
						kit.start(app, element);
					});
				}
