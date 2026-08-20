#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
WORKSPACE=${ALPS_ACCEPTANCE_WORKSPACE:-$(mktemp -d)}
FIXTURE=${ALPS_ACCEPTANCE_FIXTURE:-$(mktemp -d)}
ADDRESS=${ALPS_ACCEPTANCE_ADDRESS:-127.0.0.1:18788}
BUILD_DIR=$(mktemp -d)
BINARY="$BUILD_DIR/alps"
LOG=$(mktemp)
SSE_LOG=$(mktemp)

cleanup() {
  if [[ -n "${SERVER_PID:-}" ]]; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  rm -rf "$BUILD_DIR"
  rm -f "$LOG" "$SSE_LOG"
  if [[ -z "${ALPS_ACCEPTANCE_WORKSPACE:-}" ]]; then
    rm -rf "$WORKSPACE"
  fi
  if [[ -z "${ALPS_ACCEPTANCE_FIXTURE:-}" ]]; then
    rm -rf "$FIXTURE"
  fi
}
trap cleanup EXIT

fail() {
  echo "acceptance failure: $*" >&2
  echo "--- runtime log ---" >&2
  cat "$LOG" >&2 || true
  exit 1
}

status() {
  curl -sS -o /dev/null -w '%{http_code}' "$@"
}

wait_for_runtime() {
  for _ in $(seq 1 100); do
    if curl -fsS "http://$ADDRESS/api/health" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.1
  done
  fail "runtime did not become ready"
}

start_runtime() {
  : >"$LOG"
  "$BINARY" serve --workspace "$WORKSPACE" --root "$FIXTURE" --addr "$ADDRESS" >"$LOG" 2>&1 &
  SERVER_PID=$!
  wait_for_runtime
}

stop_runtime() {
  kill "$SERVER_PID" 2>/dev/null || true
  wait "$SERVER_PID" 2>/dev/null || true
  unset SERVER_PID
}

mkdir -p "$FIXTURE/skills/example/scripts" "$FIXTURE/.alps"
cat >"$FIXTURE/skills/example/SKILL.md" <<'SKILL'
---
name: example-skill
description: Produce a small traceable example Artifact. ALPS-conformant.
---
# Example Skill

## Purpose

Establish a locally verifiable example result.

## Outcomes

- An example result is available.
SKILL
cat >"$FIXTURE/skills/example/scripts/must-not-run.sh" <<EOF
#!/usr/bin/env bash
touch "$FIXTURE/discovery-executed"
EOF
chmod +x "$FIXTURE/skills/example/scripts/must-not-run.sh"
cat >"$FIXTURE/plugin.json" <<'JSON'
{
  "name": "example-plugin",
  "description": "Acceptance fixture plugin"
}
JSON
cat >"$FIXTURE/.alps/process-model.yaml" <<'YAML'
apiVersion: alps.dev/process-model/v1alpha1
kind: SkillModel
metadata:
  id: example-model
  name: Example Model
spec:
  processes:
    - id: example
      ref: ../skills/example/SKILL.md
  interfaces:
    - id: example-artifact
      name: Example Artifact
      kind: artifact
YAML

cd "$ROOT_DIR"
go build -o "$BINARY" ./cmd/alps
start_runtime

[[ "$(status "http://$ADDRESS/api/catalog")" == "401" ]] || fail "catalog did not reject an unauthenticated request"
TOKEN=$(tr -d '\r\n' <"$WORKSPACE/runtime/access.token")
AUTH=(-H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json")
[[ "$(status -H 'Authorization: Bearer wrong-token' "http://$ADDRESS/api/catalog")" == "401" ]] || fail "catalog accepted a wrong token"
[[ "$(status "${AUTH[@]}" -H 'Origin: http://invalid.example' -X POST "http://$ADDRESS/api/runs" -d '{"title":"Rejected","process":"Example"}')" == "403" ]] || fail "mutation accepted an invalid Origin"

CATALOG=$(curl -fsS "${AUTH[@]}" "http://$ADDRESS/api/catalog")
read -r SKILL_ID PLUGIN_COUNT MODEL_COUNT < <(python3 -c '
import json,sys
items=json.load(sys.stdin)
skills=[x for x in items if x["kind"]=="skill" and x["name"]=="example-skill"]
print(skills[0]["id"] if skills else "", sum(x["kind"]=="plugin" for x in items), sum(x["kind"]=="process-model" for x in items))
' <<<"$CATALOG")
[[ -n "$SKILL_ID" ]] || fail "fixture Skill was not discovered"
[[ "$PLUGIN_COUNT" -ge 1 ]] || fail "fixture Plugin was not discovered"
[[ "$MODEL_COUNT" -ge 1 ]] || fail "fixture Process Model was not discovered"
[[ ! -e "$FIXTURE/discovery-executed" ]] || fail "discovery executed a package script"

CONTENT=$(curl -fsS "${AUTH[@]}" "http://$ADDRESS/api/assets/$SKILL_ID/content?path=SKILL.md")
python3 -c 'import json,sys; assert "# Example Skill" in json.load(sys.stdin)["content"]' <<<"$CONTENT" || fail "Skill content was not readable"
TRAVERSAL_STATUS=$(status "${AUTH[@]}" "http://$ADDRESS/api/assets/$SKILL_ID/content?path=../plugin.json")
[[ "$TRAVERSAL_STATUS" != "200" ]] || fail "asset preview allowed path traversal"

ADOPTED=$(curl -fsS "${AUTH[@]}" -X POST "http://$ADDRESS/api/assets/$SKILL_ID/adopt" -d '{}')
REVISION_ID=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["revisionId"])' <<<"$ADOPTED")
[[ -n "$REVISION_ID" ]] || fail "adoption returned no Revision"
[[ -d "$WORKSPACE/snapshots/skill/$REVISION_ID" ]] || fail "immutable adoption snapshot was not created"

GRAPH=$(curl -fsS "${AUTH[@]}" "http://$ADDRESS/api/model")
python3 -c 'import json,sys; v=json.load(sys.stdin); assert v["processes"] and v["interfaces"] and v["edges"]' <<<"$GRAPH" || fail "Atlas graph was incomplete"

RUN_JSON=$(curl -fsS "${AUTH[@]}" -X POST "http://$ADDRESS/api/runs" -d "{\"title\":\"Acceptance Run\",\"process\":\"Example Skill\",\"assetID\":\"$SKILL_ID\"}")
read -r RUN_ID RUN_VERSION < <(python3 -c 'import json,sys; v=json.load(sys.stdin); print(v["id"],v["version"])' <<<"$RUN_JSON")
[[ -n "$RUN_ID" ]] || fail "Run was not created"

REPORT=$(curl -fsS "${AUTH[@]}" -X POST "http://$ADDRESS/api/runs/$RUN_ID/report" -d "{\"actor\":\"acceptance-agent\",\"message\":\"Artifact prepared\",\"progress\":60,\"expectedVersion\":$RUN_VERSION}")
RUN_VERSION=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["version"])' <<<"$REPORT")
[[ "$RUN_VERSION" -gt 1 ]] || fail "Run report did not advance the optimistic version"

ARTIFACT=$(curl -fsS "${AUTH[@]}" -X POST "http://$ADDRESS/api/runs/$RUN_ID/artifacts" -d '{"name":"result.txt","mediaType":"text/plain","content":"acceptance artifact"}')
ARTIFACT_ID=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["artifactId"])' <<<"$ARTIFACT")
[[ -n "$ARTIFACT_ID" ]] || fail "Artifact was not committed"
find "$WORKSPACE/blobs/sha256" -type f -size +0c | grep -q . || fail "content-addressed Artifact blob was not written"

curl -fsS "${AUTH[@]}" -X POST "http://$ADDRESS/api/runs/$RUN_ID/usage" -d '{"requested":"auto","effective":"provider-model","resolved":"actual-model","effort":"high","source":"acceptance","input":21,"output":8,"cacheRead":3,"reasoning":2}' >/dev/null

GATE=$(curl -fsS "${AUTH[@]}" -X POST "http://$ADDRESS/api/runs/$RUN_ID/gates" -d "{\"title\":\"Publish result\",\"effect\":\"Exercise a reversible local decision\",\"authority\":\"operator\",\"reversible\":true,\"expectedVersion\":$RUN_VERSION}")
GATE_ID=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<<"$GATE")
DETAIL=$(curl -fsS "${AUTH[@]}" "http://$ADDRESS/api/runs/$RUN_ID")
WAITING_VERSION=$(python3 -c 'import json,sys; v=json.load(sys.stdin); assert v["run"]["state"]=="waiting_for_decision"; print(v["run"]["version"])' <<<"$DETAIL")
[[ "$(status "${AUTH[@]}" -X POST "http://$ADDRESS/api/gates/$GATE_ID/decisions" -d "{\"decision\":\"continue\",\"actor\":\"acceptance\",\"expectedVersion\":$RUN_VERSION}")" == "409" ]] || fail "stale Decision was not rejected"
curl -fsS "${AUTH[@]}" -X POST "http://$ADDRESS/api/gates/$GATE_ID/decisions" -d "{\"decision\":\"continue\",\"actor\":\"acceptance\",\"rationale\":\"verified locally\",\"expectedVersion\":$WAITING_VERSION}" >/dev/null
FINAL=$(curl -fsS "${AUTH[@]}" "http://$ADDRESS/api/runs/$RUN_ID")
python3 -c 'import json,sys; assert json.load(sys.stdin)["run"]["state"]=="active"' <<<"$FINAL" || fail "Decision did not resume the Run"

ANALYSIS=$(curl -fsS "${AUTH[@]}" "http://$ADDRESS/api/analysis")
python3 -c 'import json,sys; v=json.load(sys.stdin); assert v["active"]>=1 and v["assets"]>=3 and v["tokens"]>=29' <<<"$ANALYSIS" || fail "Analysis did not reflect Runtime state and usage"

(curl -sN --max-time 2 "${AUTH[@]}" "http://$ADDRESS/api/events" >"$SSE_LOG" || true) &
SSE_PID=$!
sleep 0.3
curl -fsS "${AUTH[@]}" -X POST "http://$ADDRESS/api/runs" -d '{"title":"SSE Run","process":"Example Skill"}' >/dev/null
wait "$SSE_PID" || true
grep -q 'event: run.created' "$SSE_LOG" || fail "SSE did not expose persisted or live Domain Events"

MCP_OUTPUT=$(printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
  '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"alps_catalog_list","arguments":{}}}' \
  | "$BINARY" mcp --workspace "$WORKSPACE")
python3 -c '
import json,sys
rows=[json.loads(line) for line in sys.stdin if line.strip()]
assert rows[0]["result"]["protocolVersion"]=="2025-11-25"
assert any(t["name"]=="alps_run_start" for t in rows[1]["result"]["tools"])
assert len(rows[2]["result"]["structuredContent"])>=3
' <<<"$MCP_OUTPUT" || fail "MCP initialize, tool discovery, or catalog call failed"

BACKUP=$(curl -fsS "${AUTH[@]}" -X POST "http://$ADDRESS/api/admin/backup" -d '{}')
BACKUP_PATH=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["path"])' <<<"$BACKUP")
[[ -s "$BACKUP_PATH" ]] || fail "consistent SQLite backup was not created"

EXPORT=$(curl -fsS "${AUTH[@]}" "http://$ADDRESS/api/runs/$RUN_ID/export")
python3 -c 'import json,sys; v=json.load(sys.stdin); assert v["run"]["id"] and v["events"]' <<<"$EXPORT" || fail "Run audit export was incomplete"

stop_runtime
start_runtime
PERSISTED=$(curl -fsS "${AUTH[@]}" "http://$ADDRESS/api/runs/$RUN_ID")
python3 -c 'import json,sys; assert json.load(sys.stdin)["run"]["id"]' <<<"$PERSISTED" || fail "Run did not survive Runtime restart"

echo "ALPS Local Runtime acceptance test passed"
echo "Run: $RUN_ID"
echo "Revision: $REVISION_ID"
