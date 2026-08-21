//#region src/lib/format.ts
function relativeTime(value) {
	if (!value) return "";
	const seconds = Math.max(0, Math.floor((Date.now() - Date.parse(value)) / 1e3));
	if (seconds < 60) return "now";
	if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
	if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
	return `${Math.floor(seconds / 86400)}d`;
}
function number(value) {
	return typeof value === "number" ? new Intl.NumberFormat().format(value) : value == null ? "—" : String(value);
}
function humanState(value) {
	return value.replaceAll("_", " ");
}
//#endregion
export { number as n, relativeTime as r, humanState as t };
