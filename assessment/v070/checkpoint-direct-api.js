// Invoked by the coordinator in functions.exec with tools and an expected ref.
// Experiment saving only; this is not part of the ALPS distribution.
return (async () => {
  const repository = "mashimashica/alps";
  const root = "/workspace/scratch/a75c3a6d9076/alps-v070-assessment";
  const refURL = `https://api.github.com/repos/${repository}/git/ref/heads/assessment/v070-evidence`;
  const shaPattern = /^[0-9a-f]{40}$/;
  function result(r) {
    if (r.structuredContent) return r.structuredContent.result || r.structuredContent;
    for (const item of r.content || []) {
      if (item.type !== "text") continue;
      try { const parsed = JSON.parse(item.text); return parsed.result || parsed; } catch {}
    }
    throw Error("Missing structured response");
  }
  async function fetchJSON(url) {
    return JSON.parse(result(await tools.mcp__codex_apps__github_fetch({url})).content);
  }
  async function command(cmd, workdir = root, max_output_tokens = 1000) {
    const r = await tools.exec_command({cmd, workdir, max_output_tokens});
    if (r.exit_code !== 0) throw Error(r.output);
    return r.output;
  }
  if (!shaPattern.test(expected)) throw Error("Expected checkpoint SHA required");
  const parent = (await fetchJSON(refURL)).object.sha;
  if (parent !== expected) throw Error(`Ref changed; reconcile before writing: ${parent}`);
  const base = (await fetchJSON(`https://api.github.com/repos/${repository}/git/commits/${parent}`)).tree.sha;
  if (!shaPattern.test(base)) throw Error("Verified base tree missing");
  const snapshot = (await command("mktemp -d /workspace/scratch/a75c3a6d9076/assessment-checkpoint-XXXXXX")).trim();
  if (!/^\/workspace\/scratch\/a75c3a6d9076\/assessment-checkpoint-[A-Za-z0-9]+$/.test(snapshot)) throw Error("Invalid snapshot path");
  await command(`cp -a ${root}/. ${snapshot}/`);
  const details = JSON.parse(await command("python3 checkpoint.py export --cache", snapshot, 2000));
  let payload = "";
  for (let offset = 0; offset < details.characters; offset += 64000) {
    const offsets = [offset, offset + 16000, offset + 32000, offset + 48000]
      .filter(value => value < details.characters);
    // Independent reads of the immutable snapshot retain their offset order.
    const chunks = await Promise.all(offsets.map(value =>
      command(`python3 checkpoint.py slice --char-offset ${value} --char-limit 16000`, snapshot, 32768)));
    payload += chunks.join("");
  }
  if (Array.from(payload).length !== details.characters) throw Error("Export length mismatch");
  const entries = JSON.parse(payload);
  if (entries.length !== details.entries) throw Error("Export count mismatch");
  if (!entries.length) return {unchanged: true, commit: parent, tree: base, snapshot};
  const tree = result(await tools.mcp__codex_apps__github_create_tree({
    repository_full_name: repository, base_tree_sha: base, tree_elements: entries
  })).sha;
  if (!shaPattern.test(tree || "")) throw Error("Created tree SHA missing");
  const sha = result(await tools.mcp__codex_apps__github_create_commit({
    repository_full_name: repository, parent_sha: parent, tree_sha: tree,
    message: message + "\n\nSigned-off-by: Mashimashica <43808210+mashimashica@users.noreply.github.com>"
  })).sha;
  if (!shaPattern.test(sha || "")) throw Error("Created commit SHA missing");
  const commit = await fetchJSON(`https://api.github.com/repos/${repository}/git/commits/${sha}`);
  if (commit.tree.sha !== tree || commit.parents[0].sha !== parent ||
      !commit.message.includes(`Signed-off-by: ${commit.author.name} <${commit.author.email}>`)) {
    throw Error("Commit tree, parent or author-matching DCO mismatch");
  }
  await tools.mcp__codex_apps__github_update_ref({repository_full_name: repository,
    branch_name: "assessment/v070-evidence", sha, force: false});
  if ((await fetchJSON(refURL)).object.sha !== sha) throw Error("Saved ref mismatch");
  const marked = await command(`python3 checkpoint.py mark --root ${snapshot}`);
  await command(`cp ${snapshot}/.local/published-hashes.json .local/published-hashes.json`);
  return {commit: sha, tree, snapshot, entries: entries.length, marked};
})();
