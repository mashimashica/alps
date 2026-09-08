// Coordinator readback of an already-created assessment evidence checkpoint.
// Invoked with tools and cp; no remote mutation or product change.
return (async () => {
  const root = "/workspace/scratch/a75c3a6d9076/alps-v070-assessment";
  const repo = "mashimashica/alps";
  if (!/^[0-9a-f]{40}$/.test(cp.commit) || !/^[0-9a-f]{40}$/.test(cp.tree) ||
      !/^\/workspace\/scratch\/a75c3a6d9076\/assessment-checkpoint-[A-Za-z0-9]+$/.test(cp.snapshot)) {
    throw Error("Invalid checkpoint identity");
  }
  function unpack(r) {
    if (r.structuredContent) return r.structuredContent.result || r.structuredContent;
    for (const c of r.content || []) if (c.type === "text") {
      try { const p = JSON.parse(c.text); return p.result || p; } catch {}
    }
    throw Error("Missing structured response");
  }
  async function fetchJSON(url) {
    return JSON.parse(unpack(await tools.mcp__codex_apps__github_fetch({url})).content);
  }
  const expected = await tools.exec_command({workdir: cp.snapshot, max_output_tokens: 30000, cmd: `python3 - <<'PY'
import json, hashlib
from pathlib import Path
checks = []
for entry in json.loads(Path('.local/export.json').read_text()):
    raw = entry['content'].encode('utf-8')
    checks.append({'path': entry['path'], 'mode': entry['mode'], 'type': entry['type'],
                   'sha': hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\\0' + raw).hexdigest()})
print(json.dumps(checks))
PY`});
  if (expected.exit_code !== 0) throw Error(expected.output);
  const checks = JSON.parse(expected.output);
  if (checks.length !== cp.entries) throw Error("Expected changed-entry count mismatch");
  const tree = await fetchJSON(`https://api.github.com/repos/${repo}/git/trees/${cp.tree}?recursive=1`);
  if (tree.truncated || tree.sha !== cp.tree) throw Error("Tree truncated or identity differs");
  const entries = new Map(tree.tree.map(e => [e.path, e]));
  for (const check of checks) {
    const actual = entries.get(check.path);
    if (!actual || ["sha", "mode", "type"].some(k => actual[k] !== check[k])) {
      throw Error("Saved blob identity/mode/type mismatch: " + check.path);
    }
  }
  const commit = await fetchJSON(`https://api.github.com/repos/${repo}/git/commits/${cp.commit}`);
  const ref = await fetchJSON(`https://api.github.com/repos/${repo}/git/ref/heads/assessment/v070-evidence`);
  if (commit.tree.sha !== cp.tree || ref.object.sha !== cp.commit ||
      !commit.message.includes(`Signed-off-by: ${commit.author.name} <${commit.author.email}>`)) {
    throw Error("Commit, current ref or author/DCO mismatch");
  }
  const receipt = `\n- Verified ${cp.commit}, tree ${cp.tree}, parent ${commit.parents[0].sha}. Snapshot ${cp.snapshot}: ${checks.length} changed entries. Commit/tree/parent/DCO/non-force ref checked by the save operation; all changed Git blob identities, modes and types matched the complete recursive exact tree during readback. ${cp.marked.trim()}\n`;
  const quoted = "'" + receipt.replaceAll("'", "'\\''") + "'";
  const saved = await tools.exec_command({workdir: root, max_output_tokens: 500,
    cmd: "python3 -c 'import sys; from pathlib import Path; p=Path(\"checkpoints.md\"); p.open(\"a\").write(sys.argv[1])' " + quoted});
  if (saved.exit_code !== 0) throw Error(saved.output);
  return {commit: cp.commit, tree: cp.tree, matchedChangedEntries: checks.length, receiptRecorded: true};
})();
