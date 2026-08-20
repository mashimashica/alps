#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
WORKSPACE=${ALPS_SMOKE_WORKSPACE:-$(mktemp -d)}
ADDRESS=${ALPS_SMOKE_ADDRESS:-127.0.0.1:18787}
BINARY=${ALPS_SMOKE_BINARY:-$(mktemp -u)/alps}
LOG=${ALPS_SMOKE_LOG:-$(mktemp)}

cleanup() {
  if [[ -n "${SERVER_PID:-}" ]]; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  rm -f "$BINARY"
  if [[ -z "${ALPS_SMOKE_WORKSPACE:-}" ]]; then
    rm -rf "$WORKSPACE"
  fi
}
trap cleanup EXIT

cd "$ROOT_DIR"
go build -o "$BINARY" ./cmd/alps
"$BINARY" serve --workspace "$WORKSPACE" --root "$ROOT_DIR" --addr "$ADDRESS" >"$LOG" 2>&1 &
SERVER_PID=$!

for _ in $(seq 1 80); do
  if curl -fsS "http://$ADDRESS/api/health" >/dev/null; then
    break
  fi
  sleep 0.1
done
curl -fsS "http://$ADDRESS/api/health" >/dev/null
TOKEN=$(tr -d '\r\n' <"$WORKSPACE/runtime/access.token")
AUTH=(-H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json")

curl -fsS "${AUTH[@]}" "http://$ADDRESS/api/catalog" >/dev/null
RUN_JSON=$(curl -fsS "${AUTH[@]}" -X POST "http://$ADDRESS/api/runs" -d '{"title":"Smoke Run","process":"Apply Skills"}')
read -r RUN_ID RUN_VERSION < <(python3 -c 'import json,sys; v=json.load(sys.stdin); print(v["id"],v["version"])' <<<"$RUN_JSON")

GATE_JSON=$(curl -fsS "${AUTH[@]}" -X POST "http://$ADDRESS/api/runs/$RUN_ID/gates" -d "{\"title\":\"Confirm smoke action\",\"effect\":\"Exercise a reversible local decision\",\"authority\":\"operator\",\"reversible\":true,\"expectedVersion\":$RUN_VERSION}")
GATE_ID=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<<"$GATE_JSON")
DETAIL_JSON=$(curl -fsS "${AUTH[@]}" "http://$ADDRESS/api/runs/$RUN_ID")
WAITING_VERSION=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["run"]["version"])' <<<"$DETAIL_JSON")

curl -fsS "${AUTH[@]}" -X POST "http://$ADDRESS/api/gates/$GATE_ID/decisions" -d "{\"decision\":\"continue\",\"actor\":\"smoke-test\",\"rationale\":\"local smoke test\",\"expectedVersion\":$WAITING_VERSION}" >/dev/null
FINAL_STATE=$(curl -fsS "${AUTH[@]}" "http://$ADDRESS/api/runs/$RUN_ID" | python3 -c 'import json,sys; print(json.load(sys.stdin)["run"]["state"])')

if [[ "$FINAL_STATE" != "active" ]]; then
  echo "unexpected final state: $FINAL_STATE" >&2
  exit 1
fi

echo "ALPS Local Runtime smoke test passed"
echo "Run: $RUN_ID"
