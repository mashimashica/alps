const app = document.querySelector('#app');

const state = {
  route: location.hash.slice(1) || '/atlas',
  catalog: [],
  runs: [],
  gates: [],
  graph: null,
  analysis: null,
  viewer: null,
  runSheet: null,
  dialog: null,
  filter: 'all',
  search: '',
};

const icons = { atlas: '◉', runs: '▦', library: '◇', analysis: '⌁' };
const pageMeta = {
  atlas: ['Atlas', 'Process and interface relationships'],
  runs: ['Runs', 'Current work and human attention'],
  library: ['Library', 'Skills, plugins, and process models'],
  analysis: ['Analysis', 'Operational signals that change the next action'],
};

async function api(path, options = {}) {
  const response = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const value = await response.json().catch(() => ({ error: { message: response.statusText } }));
    throw new Error(value.error?.message || response.statusText);
  }
  return response.json();
}

async function load() {
  const [catalog, runs, gates, graph, analysis] = await Promise.all([
    api('/catalog'),
    api('/runs'),
    api('/gates'),
    api('/model'),
    api('/analysis'),
  ]);
  Object.assign(state, { catalog, runs, gates, graph, analysis });
  render();
}

function shell(content) {
  const key = state.route.split('/')[1] || 'atlas';
  const meta = pageMeta[key] || pageMeta.atlas;
  const navigation = Object.entries(icons).map(([name, icon]) => `
    <button class="nav ${key === name ? 'active' : ''}" data-route="/${name}" title="${capitalize(name)}" aria-label="${capitalize(name)}">${icon}</button>
  `).join('');
  return `
    <div class="app">
      <aside class="rail glass">
        <button class="brand" data-route="/atlas" aria-label="ALPS"><img src="/assets/icon.svg" alt=""></button>
        ${navigation}
        <div class="spacer"></div>
      </aside>
      <main class="shell">
        <header class="topbar">
          <div class="title"><h1>${meta[0]}</h1><p>${meta[1]}</p></div>
          <button class="command" data-command>Search or go to… <kbd>⌘K</kbd></button>
        </header>
        <section class="view">${content}</section>
      </main>
    </div>
    ${state.viewer ? skillViewer() : ''}
    ${state.runSheet ? runSheet() : ''}
    ${state.dialog ? decisionDialog() : ''}
  `;
}

function render() {
  let content = '';
  if (state.route === '/atlas') content = atlas();
  else if (state.route === '/runs') content = runBoard();
  else if (state.route === '/library') content = library();
  else if (state.route === '/analysis') content = analysis();
  else content = atlas();
  app.innerHTML = shell(content);
  bind();
}

function atlas() {
  if (!state.graph) return '<div class="empty">Loading…</div>';
  return `
    <div class="atlas glass">
      <svg viewBox="0 0 1000 650" role="img" aria-label="Process model network">${edgesSVG()}${nodesSVG()}</svg>
      <img class="atlas-center" src="/assets/icon.svg" alt="ALPS">
    </div>
  `;
}

function positions(nodes, radius, centerX = 500, centerY = 325) {
  return nodes.map((node, index) => {
    const angle = -Math.PI / 2 + index * Math.PI * 2 / nodes.length;
    return { ...node, x: centerX + Math.cos(angle) * radius, y: centerY + Math.sin(angle) * radius };
  });
}

function graphPositions() {
  const processes = positions(state.graph.processes, 245);
  const interfaces = positions(state.graph.interfaces, 112);
  return { processes, interfaces, map: Object.fromEntries([...processes, ...interfaces].map((node) => [node.id, node])) };
}

function edgesSVG() {
  const { map } = graphPositions();
  return state.graph.edges.map((edge) => {
    const from = map[edge.from];
    const to = map[edge.to];
    return from && to ? `<path class="edge" d="M ${from.x} ${from.y} Q 500 325 ${to.x} ${to.y}"></path>` : '';
  }).join('');
}

function nodesSVG() {
  const { processes, interfaces, map } = graphPositions();
  const processNodes = processes.map((node) => `
    <g class="node process" transform="translate(${node.x} ${node.y})"><circle r="34"></circle><text y="54">${escapeHTML(node.name)}</text></g>
  `).join('');
  const interfaceNodes = interfaces.map((node) => `
    <g class="node interface" transform="translate(${node.x} ${node.y})"><circle r="25"></circle><text y="4">${escapeHTML(short(node.name, 13))}</text></g>
  `).join('');
  const liveNodes = (state.graph.live || []).map((item) => {
    const node = map[item.processId];
    if (!node) return '';
    const className = item.state === 'waiting_for_decision' ? 'attention' : 'live';
    return `<circle class="${className}" cx="${node.x + 24}" cy="${node.y - 24}" r="7"><title>${escapeHTML(item.state)}</title></circle>`;
  }).join('');
  return `${processNodes}${interfaceNodes}${liveNodes}`;
}

function runBoard() {
  const lanes = {
    Now: state.runs.filter((run) => ['created', 'active'].includes(run.state)),
    Waiting: state.runs.filter((run) => run.state.startsWith('waiting_') || run.state === 'completion_requested'),
    Done: state.runs.filter((run) => ['completed', 'failed', 'cancelled'].includes(run.state)),
  };
  return `
    <div class="toolbar"><button class="primary" data-new-run>Start Run</button></div>
    <div class="board">
      ${Object.entries(lanes).map(([name, items]) => `
        <section class="lane"><h2>${name}</h2><div class="cards">${items.length ? items.map(runCard).join('') : '<div class="empty">No runs</div>'}</div></section>
      `).join('')}
    </div>
  `;
}

function runCard(run) {
  const gate = state.gates.find((item) => item.runId === run.id);
  return `
    <button class="run-card" data-run="${run.id}">
      <h3>${escapeHTML(run.title)}</h3>
      <p>${escapeHTML(run.statusText || run.process)}</p>
      ${run.progress != null ? `<progress class="progress" value="${run.progress}" max="100"></progress>` : ''}
      <div class="run-foot"><span>${gate ? '<span class="badge danger">Decision</span>' : escapeHTML(run.process)}</span><span>${ago(run.updatedAt)}</span></div>
    </button>
  `;
}

function library() {
  const items = state.catalog.filter((asset) => {
    const kindMatches = state.filter === 'all' || asset.kind === state.filter;
    const queryMatches = !state.search || `${asset.name} ${asset.description}`.toLowerCase().includes(state.search.toLowerCase());
    return kindMatches && queryMatches;
  });
  return `
    <div class="panel glass">
      <div class="toolbar">
        <input id="asset-search" placeholder="Search Skills and Plugins" value="${escapeHTML(state.search)}">
        <div class="segmented">
          ${[['all', 'All'], ['skill', 'Skills'], ['plugin', 'Plugins'], ['process-model', 'Models']].map(([key, label]) => `<button data-filter="${key}" class="${state.filter === key ? 'active' : ''}">${label}</button>`).join('')}
        </div>
      </div>
      <div class="asset-list">
        ${items.map((asset) => `
          <button class="asset-row" data-asset="${asset.id}">
            <span class="asset-icon">${asset.kind === 'skill' ? 'S' : asset.kind === 'plugin' ? 'P' : 'M'}</span>
            <span><span class="asset-name">${escapeHTML(asset.name)}</span><span class="asset-meta">${escapeHTML(asset.kind)} · ${escapeHTML(asset.scope)}</span></span>
            <span class="status">${asset.alpsState === 'changed' ? 'Changed' : asset.alpsState === 'adopted' ? 'Adopted' : '›'}</span>
          </button>
        `).join('') || '<div class="empty">No assets found</div>'}
      </div>
    </div>
  `;
}

function analysis() {
  const value = state.analysis || {};
  return `
    <div class="metrics">
      ${[['Active', value.active ?? 0], ['Waiting', value.waiting ?? 0], ['Observed tokens', formatNumber(value.tokens ?? 0)]].map(([label, metric]) => `
        <div class="metric glass"><strong>${metric}</strong><span>${label}</span></div>
      `).join('')}
    </div>
    <div class="panel glass analysis-note"><h2>Current signal</h2><p>${value.waiting ? `${value.waiting} Run${value.waiting === 1 ? ' is' : 's are'} waiting. Resolve the oldest Decision before starting more work.` : 'No Run currently requires human attention.'}</p></div>
  `;
}

function skillViewer() {
  const asset = state.viewer;
  const action = asset.alpsState === 'adopted' ? 'Start Run' : asset.alpsState === 'changed' ? 'Compare changes' : 'Adopt Skill';
  return `
    <div class="overlay">
      <section class="viewer glass" role="dialog" aria-modal="true">
        <header class="viewer-head">
          <div class="viewer-title"><span class="asset-icon">${asset.kind === 'skill' ? 'S' : asset.kind === 'plugin' ? 'P' : 'M'}</span><div><h2>${escapeHTML(asset.name)}</h2><p>${escapeHTML(asset.kind)} · ${escapeHTML(asset.scope)}</p></div></div>
          <button class="icon-button" data-close aria-label="Close">×</button>
        </header>
        <div class="viewer-body">
          <nav class="tree">${asset.files.map((file) => `<button class="${file === asset.contentPath ? 'active' : ''}" data-file="${escapeHTML(file)}">${escapeHTML(file)}</button>`).join('')}</nav>
          <article class="content"><h1>${escapeHTML(asset.name)}</h1><p>${escapeHTML(asset.description || 'No discovery description.')}</p><pre>${escapeHTML(asset.content || 'No preview available.')}</pre></article>
        </div>
        <footer class="viewer-foot"><button class="primary" data-viewer-primary="${asset.id}">${action}</button></footer>
      </section>
    </div>
  `;
}

function runSheet() {
  const detail = state.runSheet;
  const run = detail.run;
  return `
    <div class="overlay">
      <section class="viewer glass run-viewer" role="dialog" aria-modal="true">
        <header class="viewer-head">
          <div class="viewer-title"><span class="asset-icon">R</span><div><h2>${escapeHTML(run.title)}</h2><p>${escapeHTML(run.process)} · ${escapeHTML(run.state)}</p></div></div>
          <button class="icon-button" data-close aria-label="Close">×</button>
        </header>
        <article class="content">
          ${detail.gate ? `<button class="primary" data-open-gate>Review ${escapeHTML(detail.gate.title)}</button>` : ''}
          <h2>Current status</h2><p>${escapeHTML(run.statusText || run.state)}</p>
          ${run.progress != null ? `<progress class="progress" value="${run.progress}" max="100"></progress>` : ''}
          <h2>Events</h2><div class="timeline">${detail.events.map((event) => `<div><strong>${escapeHTML(event.type)}</strong><span>${ago(event.occurredAt)}</span></div>`).join('') || '<p>No events yet.</p>'}</div>
        </article>
        <footer class="viewer-foot"><button class="secondary" data-close>Close</button></footer>
      </section>
    </div>
  `;
}

function decisionDialog() {
  const { gate } = state.dialog;
  return `
    <div class="overlay">
      <section class="dialog glass" role="dialog" aria-modal="true">
        <span class="badge danger">Human decision</span><h2>${escapeHTML(gate.title)}</h2><p>${escapeHTML(gate.effect)}</p>
        <p><strong>${gate.reversible ? 'Reversible' : 'Irreversible'}</strong> · Authority: ${escapeHTML(gate.authority || 'operator')}</p>
        <div class="dialog-actions"><button class="secondary" data-decision="hold">Hold</button><button class="secondary" data-decision="change">Return for changes</button><button class="primary" data-decision="continue">Continue</button></div>
      </section>
    </div>
  `;
}

function bind() {
  document.querySelectorAll('[data-route]').forEach((button) => { button.onclick = () => go(button.dataset.route); });
  document.querySelectorAll('[data-filter]').forEach((button) => { button.onclick = () => { state.filter = button.dataset.filter; render(); }; });
  const search = document.querySelector('#asset-search');
  if (search) search.oninput = (event) => { state.search = event.target.value; render(); };
  document.querySelectorAll('[data-asset]').forEach((button) => { button.onclick = async () => { state.viewer = await api(`/assets/${button.dataset.asset}`); render(); }; });
  document.querySelectorAll('[data-file]').forEach((button) => { button.onclick = async () => { const value = await api(`/assets/${state.viewer.id}/content?path=${encodeURIComponent(button.dataset.file)}`); state.viewer.content = value.content; state.viewer.contentPath = value.path; render(); }; });
  document.querySelectorAll('[data-run]').forEach((button) => { button.onclick = async () => { state.runSheet = await api(`/runs/${button.dataset.run}`); render(); }; });
  document.querySelectorAll('[data-close]').forEach((button) => { button.onclick = () => { state.viewer = null; state.runSheet = null; state.dialog = null; render(); }; });
  document.querySelector('[data-open-gate]')?.addEventListener('click', () => { state.dialog = { run: state.runSheet.run, gate: state.runSheet.gate }; render(); });
  document.querySelectorAll('[data-decision]').forEach((button) => { button.onclick = () => decide(button.dataset.decision); });
  document.querySelectorAll('[data-new-run]').forEach((button) => { button.onclick = startRun; });
  document.querySelectorAll('[data-viewer-primary]').forEach((button) => { button.onclick = () => viewerAction(button.dataset.viewerPrimary); });
  document.querySelector('[data-command]')?.addEventListener('click', () => { const value = prompt('Go to Atlas, Runs, Library, or Analysis'); if (value) go(`/${value.toLowerCase()}`); });
}

async function decide(decision) {
  const { gate, run } = state.dialog;
  await api(`/gates/${gate.id}/decisions`, { method: 'POST', body: JSON.stringify({ decision, actor: 'local-user', rationale: '', expectedVersion: run.version }) });
  state.dialog = null;
  state.runSheet = null;
  await load();
}

async function startRun() {
  const title = prompt('Run title');
  if (!title) return;
  const process = prompt('Process or Skill', 'Apply Skills') || 'Apply Skills';
  await api('/runs', { method: 'POST', body: JSON.stringify({ title, process }) });
  await load();
}

async function viewerAction(id) {
  const asset = state.viewer;
  if (asset.alpsState === 'adopted') {
    await api('/runs', { method: 'POST', body: JSON.stringify({ title: asset.name, process: asset.name, assetID: id }) });
    state.viewer = null;
    await load();
    go('/runs');
  } else {
    await api(`/assets/${id}/adopt`, { method: 'POST', body: '{}' });
    state.viewer = await api(`/assets/${id}`);
    render();
  }
}

function go(route) { location.hash = route; }
function escapeHTML(value = '') { return String(value).replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[character]); }
function capitalize(value) { return value[0].toUpperCase() + value.slice(1); }
function short(value, length) { return value.length > length ? `${value.slice(0, length - 1)}…` : value; }
function ago(value) { const seconds = Math.max(0, (Date.now() - Date.parse(value)) / 1000); if (seconds < 60) return 'now'; if (seconds < 3600) return `${Math.floor(seconds / 60)}m`; return `${Math.floor(seconds / 3600)}h`; }
function formatNumber(value) { return new Intl.NumberFormat().format(value); }

window.addEventListener('hashchange', () => { state.route = location.hash.slice(1) || '/atlas'; render(); });
window.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') { state.viewer = null; state.runSheet = null; state.dialog = null; render(); }
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); document.querySelector('[data-command]')?.click(); }
});

const events = new EventSource('/api/events');
['catalog.scanned', 'asset.adopted', 'run.created', 'run.reported', 'gate.opened', 'decision.recorded', 'artifact.committed', 'usage.observed', 'host.observed'].forEach((type) => events.addEventListener(type, () => load()));
load().catch((error) => { app.innerHTML = `<div class="empty">${escapeHTML(error.message)}</div>`; });
