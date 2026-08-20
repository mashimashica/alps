(() => {
  const state = {
    query: '',
    kind: 'all',
    atlasMode: 'structure',
    selectedNode: null,
    selectedFile: 'SKILL.md',
    openRunId: null,
    analysisLens: 'flow'
  };

  const assets = [
    { id: 'define-alps', kind: 'skill', name: 'define-alps', title: 'Agent Lifecycle Process Skill Definition', scope: 'Project', status: 'Adopted', description: 'Identify Skill needs; design and verify assessable Skill Descriptions that conform to ALPS and the Process Framework.' },
    { id: 'apply-alps', kind: 'skill', name: 'apply-alps', title: 'Agent Lifecycle Process Skill Application', scope: 'Project', status: 'Adopted', description: 'Select, execute, and compose Skills suited to the current context of application.' },
    { id: 'manage-alps', kind: 'skill', name: 'manage-alps', title: 'Agent Lifecycle Process Skill Management', scope: 'Project', status: 'Adopted', description: 'Govern adoption, discoverability, change, retirement, tailoring, assessment, and improvement of Skill assets.' },
    { id: 'meeting-operations', kind: 'model', name: 'meeting-operations', title: 'Meeting Operations', scope: 'Project', status: 'Valid', description: 'A Process Model connecting meeting records, summaries, review, and publication.' },
    { id: 'workspace-tools', kind: 'plugin', name: 'workspace-tools', title: 'Workspace Tools', scope: 'User', status: 'External', description: 'A local plugin providing file, repository, and document capabilities.' }
  ];

  const packageFiles = [
    { id: 'SKILL.md', label: 'SKILL.md', type: 'file', depth: 0 },
    { id: 'agents', label: 'agents', type: 'folder', depth: 0, open: true },
    { id: 'agents/openai.yaml', label: 'openai.yaml', type: 'file', depth: 1 },
    { id: 'assets', label: 'assets', type: 'folder', depth: 0, open: true },
    { id: 'assets/icon.svg', label: 'icon.svg', type: 'file', depth: 1 },
    { id: 'references', label: 'references', type: 'folder', depth: 0, open: true },
    { id: 'references/ALPS-SPEC.md', label: 'ALPS-SPEC.md', type: 'file', depth: 1 },
    { id: 'references/process-framework.md', label: 'process-framework.md', type: 'file', depth: 1 },
    { id: 'references/record-templates.md', label: 'record-templates.md', type: 'file', depth: 1 },
    { id: 'references/SKILL-template.md', label: 'SKILL-template.md', type: 'file', depth: 1 },
    { id: 'scripts', label: 'scripts', type: 'folder', depth: 0, open: true },
    { id: 'scripts/check_skill_description.py', label: 'check_skill_description.py', type: 'file', depth: 1 }
  ];

  const runs = [
    { id: 'run-1042', lane: 'now', process: 'Define Skill', title: 'Verify release-note Skill', detail: 'Checking Outcome–Task traceability.', host: 'Codex', progress: 67, updated: '2m', outcomes: ['Need and context identified', 'Purpose and Outcomes aligned', 'Description requirements satisfied'], model: 'gpt-5.6-codex', tokens: '18.4k' },
    { id: 'run-1047', lane: 'now', process: 'Apply Skill', title: 'Consolidate meeting record', detail: 'Extracting decisions and action items.', host: 'Claude Code', progress: 50, updated: '6m', outcomes: ['Meeting record understood', 'Decisions identified'], model: 'claude-sonnet', tokens: '9.8k' },
    { id: 'run-1038', lane: 'waiting', process: 'Publish Summary', title: 'Publish reviewed summary', detail: 'External write requires a human decision.', host: 'Cursor', progress: 75, updated: '18m', gate: true, outcomes: ['Summary reviewed', 'Traceability confirmed'], model: 'auto → claude-sonnet', tokens: '12.1k' },
    { id: 'run-1029', lane: 'waiting', process: 'Manage Skill', title: 'Reverify workspace-tools', detail: 'Source changed after adoption.', host: 'VS Code', progress: 25, updated: '41m', outcomes: ['Change detected'], model: 'gpt-5.6', tokens: 'Not reported' },
    { id: 'run-1018', lane: 'done', process: 'Define Skill', title: 'Adopt incident-summary Skill', detail: 'Verification completed.', host: 'Copilot CLI', progress: 100, updated: '1h', outcomes: ['All declared Outcomes achieved'], model: 'gpt-5.6', tokens: '21.3k' }
  ];

  const graphNodes = [
    { id: 'define', kind: 'process', label: 'Define Skill', pos: 'p1', live: true },
    { id: 'manage', kind: 'process', label: 'Manage Skill', pos: 'p2' },
    { id: 'select', kind: 'process', label: 'Select Skill', pos: 'p3', live: true },
    { id: 'execute', kind: 'process', label: 'Execute Skill', pos: 'p4', attention: true },
    { id: 'assess', kind: 'process', label: 'Assess & Improve', pos: 'p5' },
    { id: 'orchestrate', kind: 'process', label: 'Orchestrate', pos: 'p6' },
    { id: 'tailor', kind: 'process', label: 'Tailor Skill', pos: 'p7' },
    { id: 'verify', kind: 'process', label: 'Verify Skill', pos: 'p8' },
    { id: 'verified-skill', kind: 'interface', label: 'Verified Skill', pos: 'i1' },
    { id: 'managed-skill', kind: 'interface', label: 'Managed Skill', pos: 'i2' },
    { id: 'run-output', kind: 'interface', label: 'Run Output', pos: 'i3' },
    { id: 'evidence', kind: 'interface', label: 'Evidence', pos: 'i4' },
    { id: 'change-request', kind: 'interface', label: 'Change Request', pos: 'i5' }
  ];

  const graphEdges = [
    ['define','verified-skill','M500 90 C500 135 500 165 500 195'],
    ['verify','verified-skill','M300 155 C365 175 420 188 500 195'],
    ['verified-skill','manage','M500 195 C590 190 650 170 720 155'],
    ['manage','managed-skill','M720 155 C700 215 680 245 650 273'],
    ['managed-skill','select','M650 273 C715 285 765 306 820 325'],
    ['select','execute','M820 325 C815 410 780 455 700 495'],
    ['execute','run-output','M700 495 C670 470 640 440 610 403'],
    ['run-output','orchestrate','M610 403 C520 455 420 490 300 495'],
    ['run-output','assess','M610 403 C590 500 545 545 500 565'],
    ['assess','evidence','M500 565 C455 500 420 450 390 403'],
    ['evidence','tailor','M390 403 C315 405 245 380 180 325'],
    ['tailor','change-request','M180 325 C250 290 300 270 350 273'],
    ['change-request','define','M350 273 C395 190 430 130 500 90']
  ];

  const nodeInfo = {
    define: ['Define Skill', 'Establishes an assessable and usable Skill Description.', '1 active Run'],
    manage: ['Manage Skill', 'Governs adoption, change, retirement, and improvement.', 'No active Run'],
    select: ['Select Skill', 'Determines the Skill and form of application.', '1 active Run'],
    execute: ['Execute Skill', 'Applies a Skill Instance and establishes its Outcomes.', '1 human decision'],
    assess: ['Assess & Improve', 'Uses measures, evidence, and lessons to improve Skills.', 'No active Run'],
    orchestrate: ['Orchestrate', 'Connects Outputs and Inputs across multiple Skills.', 'No active Run'],
    tailor: ['Tailor Skill', 'Adapts Skills to context, risk, and constraints.', 'No active Run'],
    verify: ['Verify Skill', 'Confirms description conformance and Outcome achievability.', 'No active Run'],
    'verified-skill': ['Verified Skill', 'Output from definition and verification.', '2 connected Processes'],
    'managed-skill': ['Managed Skill', 'A discoverable Skill in a controlled state.', '2 connected Processes'],
    'run-output': ['Run Output', 'Artifacts or information produced by execution.', '3 connected Processes'],
    evidence: ['Evidence', 'Information used for assessment and decisions.', '2 connected Processes'],
    'change-request': ['Change Request', 'A request to redefine or reverify a Skill.', '2 connected Processes']
  };

  const analyses = {
    flow: { title: 'Flow', text: 'Runの流れと待機時間を確認します。', metrics: [['WIP','4'],['Median cycle','18m'],['Waiting','31%']], points: '0,215 80,190 160,198 240,145 320,160 400,112 480,124 560,82 640,96 720,58 800,72', insights: [['Waiting','Publish Summary が18分間、判断を待っています。','Open'],['Rework','Definition Processの再実行は過去7日で2件です。','Review'],['Throughput','完了Runは前週比で安定しています。','Stable']] },
    quality: { title: 'Quality', text: 'Outcome、Handoff、再作業の傾向を確認します。', metrics: [['Outcome rate','92%'],['Handoff accepted','88%'],['Rework','7%']], points: '0,170 80,165 160,145 240,150 320,122 400,118 480,110 560,84 640,94 720,72 800,62', insights: [['Traceability','2件のRunでsource mappingが不足しています。','Inspect'],['Handoff','Meeting Summaryの受入率が最も低い状態です。','Open'],['Outcome','管理ProcessのOutcome達成率は安定しています。','Stable']] },
    oversight: { title: 'Oversight', text: 'Human Decisionの必要性と待機を確認します。', metrics: [['Open gates','1'],['Median wait','11m'],['Stale decisions','0']], points: '0,210 80,175 160,185 240,130 320,160 400,142 480,148 560,108 640,130 720,88 800,118', insights: [['Decision','Publish Summary がhuman decisionを待っています。','Decide'],['Coverage','高影響操作はすべてRuntime Gateを通過しています。','Good'],['Fatigue','承認要求の重複は検出されていません。','Good']] },
    usage: { title: 'Usage', text: 'モデル利用と計測カバレッジを確認します。', metrics: [['Tokens','61.6k'],['Cache read','38%'],['Reported','80%']], points: '0,218 80,175 160,155 240,180 320,124 400,140 480,98 560,126 640,78 720,96 800,54', insights: [['Measurement','VS Codeの1 Runではtoken usageが未報告です。','Inspect'],['Resolved model','Auto routingは3 Runで使用されています。','Open'],['Cache','Claude Codeのcache read比率が最も高い状態です。','Good']] }
  };

  const pageMeta = { atlas: ['Atlas','Process Model'], runs: ['Runs','Process Instances'], library: ['Library','Skills · Plugins · Models'], analysis: ['Analysis','Operational lenses'] };

  const icon = (name, cls='') => `<svg class="icon ${cls}" aria-hidden="true"><use href="#i-${name}"></use></svg>`;
  const esc = (v) => String(v).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#039;');
  const cap = (v) => v ? v[0].toUpperCase() + v.slice(1) : '';

  function route() {
    const parts = (location.hash.replace(/^#\/?/,'') || 'atlas').split('/').filter(Boolean);
    return { page: parts[0] || 'atlas', detail: parts[1] || null };
  }

  function navLink(id, label, current) {
    return `<a class="nav-link" href="#/${id}"${current===id?' aria-current="page"':''}>${icon(id)}<span class="nav-tooltip">${label}</span></a>`;
  }

  function shell(content, page) {
    const meta = pageMeta[page];
    return `<div class="app-shell">
      <aside class="rail" aria-label="Primary navigation">
        <button class="brand-button" data-action="atlas" aria-label="Open Atlas"><img src="../../../assets/icon.svg" alt=""></button>
        <nav class="rail-nav">${navLink('atlas','Atlas',page)}${navLink('runs','Runs',page)}${navLink('library','Library',page)}${navLink('analysis','Analysis',page)}</nav>
        <div class="rail-spacer"></div><span class="runtime-dot" title="Runtime connected"></span>
        <button class="icon-button" data-action="settings" aria-label="Settings">${icon('settings')}</button>
      </aside>
      <main class="main-shell">
        <header class="topbar"><div class="page-identity"><h1>${meta[0]}</h1><span>${meta[1]}</span></div><div class="topbar-spacer"></div>
          <button class="button outline command-trigger" data-action="command">${icon('search','sm')}<span>Search or go to…</span><kbd>⌘K</kbd></button>
        </header>${content}
      </main></div>`;
  }

  function render() {
    const r = route();
    const page = pageMeta[r.page] ? r.page : 'atlas';
    const content = page==='atlas' ? atlasPage() : page==='runs' ? runsPage() : page==='library' ? libraryPage() : analysisPage();
    document.querySelector('#app').innerHTML = shell(content,page);
    bindShell();
    if (page==='atlas') bindAtlas();
    if (page==='runs') bindRuns();
    if (page==='library') bindLibrary();
    if (page==='analysis') bindAnalysis();
    if (page==='library' && r.detail) openAsset(r.detail);
  }

  function libraryPage() {
    const list = assets.filter(a => (!state.query || `${a.name} ${a.title} ${a.description}`.toLowerCase().includes(state.query.toLowerCase())) && (state.kind==='all' || a.kind===state.kind));
    const segments = ['all','skill','plugin','model'].map(v => `<button data-kind="${v}" aria-pressed="${state.kind===v}">${v==='all'?'All':cap(v)+'s'}</button>`).join('');
    return `<section class="page"><div class="library-shell"><div class="page-heading"><div><h2>Library</h2><p>利用可能な資産を開き、必要なときだけ詳細を確認します。</p></div></div>
      <div class="library-toolbar"><label class="input-wrap">${icon('search','sm')}<input class="input" id="asset-search" type="search" placeholder="Search assets" value="${esc(state.query)}"></label><div class="segmented">${segments}</div></div>
      <div class="card asset-list">${list.length ? list.map(assetRow).join('') : '<div class="empty-state">No matching assets.</div>'}</div></div></section>`;
  }

  function assetRow(a) {
    const mark = a.kind==='skill' ? '<img src="../../../assets/icon.svg" alt="">' : icon(a.kind==='model'?'atlas':'settings');
    const status = a.status==='External' ? '<span class="badge amber">External</span>' : '';
    return `<button class="asset-row" data-asset="${a.id}"><span class="asset-icon">${mark}</span><span class="asset-title"><strong>${esc(a.name)}</strong><span>${cap(a.kind)} · ${a.scope}</span></span><span class="asset-status">${status}${icon('chevron','sm')}</span></button>`;
  }

  function atlasPage() {
    const modes = ['structure','live','flow'].map(v => `<button data-mode="${v}" aria-pressed="${state.atlasMode===v}">${cap(v)}</button>`).join('');
    return `<section class="page edge atlas-page"><div class="atlas-toolbar segmented">${modes}</div><div class="atlas-canvas">
      <svg class="network-svg" viewBox="0 0 1000 650" preserveAspectRatio="none">${graphEdges.map(edgePath).join('')}</svg>
      <div class="atlas-mark"><img src="../../../assets/icon.svg" alt="ALPS"></div>${graphNodes.map(graphNode).join('')}</div>${atlasInspector()}</section>`;
  }

  function edgePath(e,i) {
    const active = state.selectedNode && (e[0]===state.selectedNode || e[1]===state.selectedNode);
    const muted = state.selectedNode && !active;
    return `<path class="network-edge" data-active="${Boolean(active)}" data-muted="${Boolean(muted)}" d="${e[2]}"></path>`;
  }

  function connected(a,b) { return graphEdges.some(e => (e[0]===a&&e[1]===b)||(e[0]===b&&e[1]===a)); }

  function graphNode(n) {
    const selected = state.selectedNode===n.id;
    const muted = state.selectedNode && !selected && !connected(state.selectedNode,n.id);
    const dot = state.atlasMode==='structure' ? '' : (n.attention ? '<span class="graph-live-dot attention"></span>' : n.live ? '<span class="graph-live-dot"></span>' : '');
    const content = n.kind==='process' ? `<strong>${n.label}</strong>` : n.label;
    return `<button class="graph-node ${n.pos}" data-kind="${n.kind}" data-node="${n.id}" data-selected="${selected}" data-muted="${Boolean(muted)}">${content}${dot}</button>`;
  }

  function atlasInspector() {
    if (!state.selectedNode) return '';
    const info = nodeInfo[state.selectedNode];
    return `<aside class="atlas-inspector card"><h3>${info[0]}</h3><p>${info[1]}</p><div class="inspector-list"><div class="inspector-row"><span>Status</span><strong>${info[2]}</strong></div></div></aside>`;
  }

  function runsPage() {
    return `<section class="page"><div class="page-heading"><div><h2>Runs</h2><p>今動いているもの、止まっているもの、完了したものだけを表示します。</p></div></div><div class="board">${boardColumn('now','Now')}${boardColumn('waiting','Waiting')}${boardColumn('done','Done')}</div></section>`;
  }

  function boardColumn(lane,label) {
    const list = runs.filter(r=>r.lane===lane);
    return `<section class="board-column card"><header class="board-column-header"><h3>${label}</h3><span>${list.length}</span></header><div class="board-list">${list.map(runCard).join('')}</div></section>`;
  }

  function runCard(r) {
    return `<button class="run-card" data-run="${r.id}"><div class="run-card-kicker"><span>${r.process}</span>${r.gate?'<span class="badge amber">Decision</span>':''}</div><h4>${r.title}</h4><p>${r.detail}</p><div class="run-card-footer"><div class="run-progress"><span class="p${r.progress}"></span></div><small>${r.updated}</small></div></button>`;
  }

  function analysisPage() {
    const a = analyses[state.analysisLens];
    const tabs = Object.keys(analyses).map(v => `<button data-lens="${v}" aria-pressed="${state.analysisLens===v}">${cap(v)}</button>`).join('');
    return `<section class="page"><div class="analysis-shell"><div class="page-heading"><div><h2>Analysis</h2><p>一度に一つの問いだけを確認します。</p></div></div><article class="analysis-card card"><header class="analysis-header"><div><h3>${a.title}</h3><p>${a.text}</p></div><div class="segmented">${tabs}</div></header><div class="metric-strip">${a.metrics.map(m=>`<div class="metric"><span>${m[0]}</span><strong>${m[1]}</strong></div>`).join('')}</div><div class="analysis-chart"><svg viewBox="0 0 800 260" preserveAspectRatio="none"><path class="chart-grid" d="M0 55H800M0 130H800M0 205H800"></path><polyline class="chart-area" points="${a.points} 800,260 0,260"></polyline><polyline class="chart-line" points="${a.points}"></polyline></svg></div><div class="insight-list">${a.insights.map(x=>`<div class="insight-row"><span class="badge">${x[0]}</span><strong>${x[1]}</strong><button class="button ghost" data-action="insight">${x[2]}</button></div>`).join('')}</div></article></div></section>`;
  }

  function bindShell() {
    document.querySelector('[data-action="atlas"]')?.addEventListener('click',()=>location.hash='#/atlas');
    document.querySelector('[data-action="command"]')?.addEventListener('click',openCommand);
    document.querySelector('[data-action="settings"]')?.addEventListener('click',()=>toast('Settings stay outside the primary flow.'));
  }

  function bindLibrary() {
    const search = document.querySelector('#asset-search');
    search?.addEventListener('input',e=>{ state.query=e.target.value; render(); requestAnimationFrame(()=>{ const el=document.querySelector('#asset-search'); el?.focus(); el?.setSelectionRange(state.query.length,state.query.length); }); });
    document.querySelectorAll('[data-kind]').forEach(b=>b.addEventListener('click',()=>{ state.kind=b.dataset.kind; render(); }));
    document.querySelectorAll('[data-asset]').forEach(b=>b.addEventListener('click',()=>location.hash=`#/library/${b.dataset.asset}`));
  }

  function bindAtlas() {
    document.querySelectorAll('[data-mode]').forEach(b=>b.addEventListener('click',()=>{ state.atlasMode=b.dataset.mode; render(); }));
    document.querySelectorAll('[data-node]').forEach(b=>b.addEventListener('click',()=>{ state.selectedNode=state.selectedNode===b.dataset.node?null:b.dataset.node; render(); }));
  }

  function bindRuns() { document.querySelectorAll('[data-run]').forEach(b=>b.addEventListener('click',()=>openRun(b.dataset.run))); }
  function bindAnalysis() {
    document.querySelectorAll('[data-lens]').forEach(b=>b.addEventListener('click',()=>{ state.analysisLens=b.dataset.lens; render(); }));
    document.querySelectorAll('[data-action="insight"]').forEach(b=>b.addEventListener('click',()=>toast('The related Run or Model would open here.')));
  }

  function openAsset(id) {
    const a = assets.find(x=>x.id===id);
    if (!a) return;
    if (a.kind!=='skill') { toast(`${cap(a.kind)} details use the same focused viewer pattern.`); return; }
    document.querySelector('#overlay').innerHTML = `<div class="overlay-backdrop" data-backdrop="asset"><section class="asset-viewer" role="dialog" aria-modal="true" aria-labelledby="asset-title"><header class="asset-viewer-header"><div class="asset-viewer-mark"><img src="../../../assets/icon.svg" alt=""></div><div class="asset-viewer-heading"><h2 id="asset-title">${esc(a.name)}</h2><p>Skill · ${a.scope}</p></div><div class="asset-viewer-actions"><button class="icon-button" data-action="asset-more" aria-label="More">${icon('more')}</button><button class="icon-button" data-action="close-asset" aria-label="Close">${icon('close')}</button></div></header><div class="asset-viewer-body"><nav class="package-tree">${packageFiles.map(fileRow).join('')}</nav><div class="file-view" id="file-view">${fileContent(a,state.selectedFile)}</div></div><footer class="asset-viewer-footer"><button class="button primary" data-action="start-run">${icon('play','sm')}Start run</button></footer></section></div>`;
    document.querySelector('[data-action="close-asset"]')?.addEventListener('click',closeAsset);
    document.querySelector('[data-backdrop="asset"]')?.addEventListener('click',e=>{ if(e.target===e.currentTarget) closeAsset(); });
    document.querySelector('[data-action="asset-more"]')?.addEventListener('click',()=>toast('Source, validation, and revision details stay behind this menu.'));
    document.querySelector('[data-action="start-run"]')?.addEventListener('click',()=>{ closeAsset(); location.hash='#/runs'; toast(`Started a new Run for ${a.name}.`); });
    document.querySelectorAll('[data-file]').forEach(b=>b.addEventListener('click',()=>{ const f=packageFiles.find(x=>x.id===b.dataset.file); if(!f||f.type==='folder')return; state.selectedFile=f.id; document.querySelectorAll('[data-file]').forEach(x=>x.setAttribute('aria-current',String(x.dataset.file===state.selectedFile))); document.querySelector('#file-view').innerHTML=fileContent(a,state.selectedFile); }));
  }

  function fileRow(f) {
    const mark = f.type==='folder' ? `${icon('chevron','tree-caret')}${icon('folder','sm')}` : icon('file','sm');
    return `<button class="tree-row" data-file="${f.id}" data-depth="${f.depth}" data-open="${Boolean(f.open)}" aria-current="${state.selectedFile===f.id}">${mark}<span>${f.label}</span></button>`;
  }

  function fileContent(a,id) {
    if(id==='SKILL.md') return `<dl class="discovery-card"><dt>Name</dt><dd>${esc(a.name)}</dd><dt>Description</dt><dd>${esc(a.description)}</dd></dl><article class="skill-document"><h1>${esc(a.title)}</h1><h2>Purpose</h2><p>The purpose of this Skill is to establish an assessable and usable Skill Description that satisfies identified stakeholder needs.</p><h2>Outcomes</h2><p>A successful application establishes the following conditions:</p><ul><li>The need to be addressed as a Skill and the intended contexts of use are identified.</li><li>The Skill Purpose, Outcomes, and boundary are aligned with the selected need.</li><li>The Skill Description satisfies applicable ALPS description requirements.</li><li>Elements and exchanges with external parties are traceable.</li></ul><h2>Activities</h2><h3>Skill Need Identification</h3><p>Identify stakeholder expectations, existing assets, risks, benefits, and the rationale for selecting the need.</p><h3>Skill Design</h3><p>Establish the boundary, write the Purpose and Outcomes, classify elements, and maintain traceability.</p><h3>Skill Verification</h3><p>Review the description against agreed criteria and confirm Outcome achievability.</p></article>`;
    if(id==='assets/icon.svg') return `<article class="skill-document"><h1>icon.svg</h1><p>The package icon used for discovery and presentation.</p><div class="asset-viewer-mark"><img src="../../../assets/icon.svg" alt="ALPS icon"></div></article>`;
    const snippets = {
      'agents/openai.yaml':'interface:\n  display_name: Define ALPS Skill\n  short_description: Design and verify ALPS-conformant Skill Descriptions\n',
      'references/ALPS-SPEC.md':'# ALPS Specification\n\nThe authoritative specification for Skill descriptions, life cycle management, tailoring, assessment, and conformance.\n',
      'references/process-framework.md':'# Process Framework\n\nA reusable basis for describing Process intent, boundaries, work content, context, relationships, and evaluation.\n',
      'references/record-templates.md':'# Record Templates\n\nOptional records for verification, decision gates, evidence, and handoffs.\n',
      'references/SKILL-template.md':'---\nname: <skill-name>\ndescription: <what it does and when to use it>\n---\n\n# <Skill title>\n\n## Purpose\n\n## Outcomes\n',
      'scripts/check_skill_description.py':'#!/usr/bin/env sh\nset -eu\nexec alps validate "$1"\n'
    };
    return `<article class="skill-document"><h1>${esc(id)}</h1><pre class="code-view">${esc(snippets[id]||'Folder')}</pre></article>`;
  }

  function closeAsset() { document.querySelector('#overlay').innerHTML=''; state.selectedFile='SKILL.md'; if(route().page==='library'&&route().detail) location.hash='#/library'; }

  function openRun(id) {
    const r=runs.find(x=>x.id===id); if(!r)return; state.openRunId=id;
    document.querySelector('#overlay').innerHTML=`<div class="sheet-backdrop" data-sheet-backdrop></div><aside class="run-sheet" role="dialog" aria-modal="true"><header class="run-sheet-header"><div><h2>${r.title}</h2><p>${r.process} · ${r.id}</p></div><button class="icon-button" data-action="close-run">${icon('close')}</button></header><div class="run-sheet-body">${r.gate?'<section class="run-section"><button class="button primary" data-action="decision">Review human decision</button></section>':''}<section class="run-section"><h3>Outcomes</h3><div class="outcome-list">${r.outcomes.map(o=>`<div class="outcome-row">${icon('check','sm')}<span>${o}</span></div>`).join('')}</div></section><section class="run-section"><h3>Context</h3><div class="run-meta-grid"><div class="run-meta-item"><span>Host</span><strong>${r.host}</strong></div><div class="run-meta-item"><span>Progress</span><strong>${r.progress}%</strong></div><div class="run-meta-item"><span>Model</span><strong>${r.model}</strong></div><div class="run-meta-item"><span>Tokens</span><strong>${r.tokens}</strong></div></div></section><section class="run-section"><h3>Timeline</h3><div class="timeline-list"><div class="timeline-row"><time>10:31</time><span>ALPS · Run started</span></div><div class="timeline-row"><time>10:32</time><span>${r.host} · Progress reported</span></div>${r.gate?'<div class="timeline-row"><time>10:33</time><span>ALPS · Decision Gate opened</span></div>':''}</div></section></div></aside>`;
    document.querySelector('[data-action="close-run"]')?.addEventListener('click',closeOverlay);
    document.querySelector('[data-sheet-backdrop]')?.addEventListener('click',closeOverlay);
    document.querySelector('[data-action="decision"]')?.addEventListener('click',()=>openDecision(r));
  }

  function openDecision(r) {
    document.querySelector('#overlay').innerHTML=`<div class="overlay-backdrop" data-decision-backdrop><section class="decision-dialog" role="dialog" aria-modal="true"><header class="decision-header"><span class="decision-symbol">${icon('alert')}</span><div><h2>Publish reviewed summary</h2><p>${r.id} · Human Decision</p></div><button class="icon-button" data-action="close-decision">${icon('close')}</button></header><div class="decision-body"><p class="decision-summary">The reviewed summary will be written to a shared project repository.</p><div class="decision-fact"><span>Effect</span><strong>External write</strong></div><div class="decision-fact"><span>Reversible</span><strong>Yes</strong></div><div class="decision-fact"><span>Verified</span><strong>Outcomes and traceability</strong></div><div class="decision-fact"><span>Unknown</span><strong>One statement remains unverified</strong></div></div><footer class="decision-footer"><button class="button ghost" data-decision="hold">Hold</button><button class="button outline" data-decision="change">Return for changes</button><button class="button primary" data-decision="continue">Publish summary</button></footer></section></div>`;
    document.querySelector('[data-action="close-decision"]')?.addEventListener('click',closeOverlay);
    document.querySelector('[data-decision-backdrop]')?.addEventListener('click',e=>{if(e.target===e.currentTarget)closeOverlay();});
    document.querySelectorAll('[data-decision]').forEach(b=>b.addEventListener('click',()=>{ const d=b.dataset.decision; closeOverlay(); if(d==='continue'){r.lane='now';r.gate=false;r.detail='Decision recorded. Ready to continue.';toast('Decision recorded. The Run can continue.');render();}else toast(d==='change'?'Run returned for changes.':'Run remains on hold.'); }));
  }

  function openCommand() {
    document.querySelector('#overlay').innerHTML=`<div class="overlay-backdrop" data-command-backdrop><section class="command-dialog" role="dialog" aria-modal="true"><input class="command-input" id="command-input" placeholder="Search pages or assets" autocomplete="off"><div class="command-list" id="command-list">${commandItems('')}</div></section></div>`;
    const input=document.querySelector('#command-input'); requestAnimationFrame(()=>input?.focus());
    input?.addEventListener('input',()=>{document.querySelector('#command-list').innerHTML=commandItems(input.value);bindCommands();});
    document.querySelector('[data-command-backdrop]')?.addEventListener('click',e=>{if(e.target===e.currentTarget)closeOverlay();}); bindCommands();
  }

  function commandItems(q) {
    const list=[['atlas','Open Atlas'],['runs','Open Runs'],['library','Open Library'],['analysis','Open Analysis'],['skill','Open define-alps']].filter(x=>x[1].toLowerCase().includes(q.toLowerCase()));
    return list.map(x=>`<button class="command-item" data-command="${x[0]}">${icon(x[0]==='skill'?'library':x[0])}<span>${x[1]}</span></button>`).join('');
  }
  function bindCommands(){document.querySelectorAll('[data-command]').forEach(b=>b.addEventListener('click',()=>{const id=b.dataset.command;closeOverlay();location.hash=id==='skill'?'#/library/define-alps':`#/${id}`;}));}
  function closeOverlay(){document.querySelector('#overlay').innerHTML='';state.openRunId=null;}
  function toast(msg){const el=document.createElement('div');el.className='toast';el.textContent=msg;document.querySelector('#toasts').append(el);setTimeout(()=>el.remove(),2600);}

  window.addEventListener('hashchange',()=>{closeOverlay();render();});
  window.addEventListener('keydown',e=>{if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();openCommand();}if(e.key==='Escape'){if(route().page==='library'&&route().detail)closeAsset();else closeOverlay();}});
  render();
})();
