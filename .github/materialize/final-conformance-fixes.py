from pathlib import Path
import json


def replace(path: str, old: str, new: str) -> None:
    file = Path(path)
    value = file.read_text()
    if old not in value:
        raise SystemExit(f"missing pattern in {path}: {old[:120]!r}")
    file.write_text(value.replace(old, new))


replace(
    "internal/runtime/runs.go",
    '''\t\treport := RunReport{ID: newID("report"), RunID: id, Actor: input.Actor, Message: input.Message, Progress: input.Progress, Claims: input.Claims, Evidence: input.Evidence, CreatedAt: timestamp}\n\t\tif _, err := tx.ExecContext(ctx, `INSERT INTO run_reports(id,run_id,actor,message,progress,claims_json,evidence_json,created_at) VALUES(?,?,?,?,?,?,?,?)`, report.ID, id, report.Actor, report.Message, report.Progress, marshal(report.Claims), marshal(report.Evidence), report.CreatedAt); err != nil {\n\t\t\treturn err\n\t\t}\n\t\tevent, err = appendEventTx(ctx, tx, actor, "run", id, "run.reported", id, "", "v1", map[string]any{"report": report, "version": newVersion})\n''',
    '''\t\treport := RunReport{ID: newID("report"), RunID: id, Actor: input.Actor, Message: input.Message, Progress: input.Progress, Claims: input.Claims, Evidence: input.Evidence, CreatedAt: timestamp}\n\t\tif _, err := tx.ExecContext(ctx, `INSERT INTO run_reports(id,run_id,actor,message,progress,claims_json,evidence_json,created_at) VALUES(?,?,?,?,?,?,?,?)`, report.ID, id, report.Actor, report.Message, report.Progress, marshal(report.Claims), marshal(report.Evidence), report.CreatedAt); err != nil {\n\t\t\treturn err\n\t\t}\n\t\tfor _, outcome := range claimedOutcomeNames(input.Claims) {\n\t\t\tif _, err := tx.ExecContext(ctx, `UPDATE run_outcomes SET status='agent_reported',evidence_json=?,updated_at=? WHERE run_id=? AND status IN ('unassessed','agent_reported') AND (id=? OR name=?)`, marshal(input.Evidence), timestamp, id, outcome, outcome); err != nil {\n\t\t\t\treturn err\n\t\t\t}\n\t\t}\n\t\tevent, err = appendEventTx(ctx, tx, actor, "run", id, "run.reported", id, "", "v1", map[string]any{"report": report, "version": newVersion})\n''',
)
replace(
    "internal/runtime/runs.go",
    '''func (r *Runtime) RequestCompletion(ctx context.Context, id string, expected int64) (Run, error) {''',
    '''func claimedOutcomeNames(claims map[string]any) []string {\n\tseen := map[string]struct{}{}\n\tvar result []string\n\tadd := func(value string) {\n\t\tvalue = strings.TrimSpace(value)\n\t\tif value == "" {\n\t\t\treturn\n\t\t}\n\t\tif _, exists := seen[value]; exists {\n\t\t\treturn\n\t\t}\n\t\tseen[value] = struct{}{}\n\t\tresult = append(result, value)\n\t}\n\tif value, ok := claims["outcome"].(string); ok {\n\t\tadd(value)\n\t}\n\tswitch values := claims["outcomes"].(type) {\n\tcase []string:\n\t\tfor _, value := range values {\n\t\t\tadd(value)\n\t\t}\n\tcase []any:\n\t\tfor _, current := range values {\n\t\t\tswitch value := current.(type) {\n\t\t\tcase string:\n\t\t\t\tadd(value)\n\t\t\tcase map[string]any:\n\t\t\t\tif id, ok := value["id"].(string); ok {\n\t\t\t\t\tadd(id)\n\t\t\t\t}\n\t\t\t\tif name, ok := value["name"].(string); ok {\n\t\t\t\t\tadd(name)\n\t\t\t\t}\n\t\t\t}\n\t\t}\n\t}\n\treturn result\n}\n\nfunc (r *Runtime) RequestCompletion(ctx context.Context, id string, expected int64) (Run, error) {''',
)
replace(
    "internal/mcp/mcp.go",
    '''type assessmentInput struct {\n\tRunID            string     `json:"runId"`\n\tSubjectType      string     `json:"subjectType"`\n\tSubjectID        string     `json:"subjectId"`\n\tAssessmentType   string     `json:"assessmentType"`\n\tCriteriaRevision string     `json:"criteriaRevision,omitempty"`\n\tResult           string     `json:"result"`\n\tOutcomeStatus    string     `json:"outcomeStatus,omitempty"`\n\tEvidence         []evidence `json:"evidence,omitempty"`\n}\n''',
    '''type assessmentInput struct {\n\tRunID            string     `json:"runId"`\n\tSubjectType      string     `json:"subjectType"`\n\tSubjectID        string     `json:"subjectId"`\n\tAssessmentType   string     `json:"assessmentType"`\n\tCriteriaRevision string     `json:"criteriaRevision,omitempty"`\n\tResult           string     `json:"result"`\n\tRationale        string     `json:"rationale,omitempty"`\n\tEvidence         []evidence `json:"evidence,omitempty"`\n}\n''',
)
replace(
    "internal/mcp/mcp.go",
    '''type handoffInput struct {\n\tProviderRunID    string     `json:"providerRunId"`\n\tProviderArtifact string     `json:"providerArtifact"`\n\tRecipientRunID   string     `json:"recipientRunId,omitempty"`\n\tRecipientInput   string     `json:"recipientInput"`\n\tInterfaceID      string     `json:"interfaceId,omitempty"`\n\tCriteriaRevision string     `json:"criteriaRevision,omitempty"`\n\tStatus           string     `json:"status,omitempty"`\n\tEvidence         []evidence `json:"evidence,omitempty"`\n}\n''',
    '''type handoffInput struct {\n\tProviderRunID      string     `json:"providerRunId"`\n\tProviderArtifactID string     `json:"providerArtifactId"`\n\tRecipientRunID     string     `json:"recipientRunId,omitempty"`\n\tRecipientProcessID string     `json:"recipientProcessId,omitempty"`\n\tRecipientInput     string     `json:"recipientInput"`\n\tCriteriaRevision   string     `json:"criteriaRevision,omitempty"`\n\tStatus             string     `json:"status,omitempty"`\n\tEvidence           []evidence `json:"evidence,omitempty"`\n}\n''',
)
replace(
    "internal/runtime/runtime.go",
    '''\t"path/filepath"\n\t"strings"\n\t"sync"''',
    '''\t"path/filepath"\n\t"strconv"\n\t"strings"\n\t"sync"''',
)
replace(
    "internal/runtime/runtime.go",
    '''\tdatabase, err := sql.Open("sqlite", databasePath)\n\tif err != nil {\n\t\treturn nil, err\n\t}\n\tdatabase.SetMaxOpenConns(8)''',
    '''\tdatabase, err := sql.Open("sqlite", databasePath)\n\tif err != nil {\n\t\treturn nil, err\n\t}\n\tif err := requireSQLiteVersion(database, 3, 51, 3); err != nil {\n\t\t_ = database.Close()\n\t\treturn nil, err\n\t}\n\tdatabase.SetMaxOpenConns(8)''',
)
replace(
    "internal/runtime/runtime.go",
    '''func ensureToken(path string) (string, error) {''',
    '''func requireSQLiteVersion(database *sql.DB, minimum ...int) error {\n\tvar raw string\n\tif err := database.QueryRow(`SELECT sqlite_version()`).Scan(&raw); err != nil {\n\t\treturn fmt.Errorf("read SQLite version: %w", err)\n\t}\n\tparts := strings.Split(raw, ".")\n\tcurrent := make([]int, len(minimum))\n\tfor index := range current {\n\t\tif index >= len(parts) {\n\t\t\tbreak\n\t\t}\n\t\tvalue, err := strconv.Atoi(parts[index])\n\t\tif err != nil {\n\t\t\treturn fmt.Errorf("invalid SQLite version %q: %w", raw, err)\n\t\t}\n\t\tcurrent[index] = value\n\t}\n\tfor index := range minimum {\n\t\tif current[index] > minimum[index] {\n\t\t\treturn nil\n\t\t}\n\t\tif current[index] < minimum[index] {\n\t\t\treturn fmt.Errorf("SQLite %d.%d.%d or later is required; found %s", minimum[0], minimum[1], minimum[2], raw)\n\t\t}\n\t}\n\treturn nil\n}\n\nfunc ensureToken(path string) (string, error) {''',
)
main = Path("cmd/alps/main.go")
value = main.read_text()
value = value.replace('''import (\n\t"context"''', '''import (\n\t"bytes"\n\t"context"''')
value = value.replace('''\t"strings"\n''', '''\t"strings"\n\t"time"\n''')
value = value.replace('postCommand(os.Args[2:], "/api/discovery/scan", map[string]any{})', 'postCommand(os.Args[2:], "/v1/discovery/scan", map[string]any{})')
value = value.replace('postCommand(os.Args[2:], "/api/admin/backup", map[string]any{})', 'postCommand(os.Args[2:], "/v1/admin/backup", map[string]any{})')
value = value.replace('fmt.Println("alps local-runtime-v0 experimental")', 'fmt.Println("alps local-runtime-v0 review")')
value = value.replace('''\tpayload := map[string]any{"host": *host, "event": *event, "raw": json.RawMessage(raw)}\n\ttoken, _ := os.ReadFile(filepath.Join(*workspace, "runtime", "access.token"))\n\treturn postJSON(endpoint+"/api/host-observations", payload, strings.TrimSpace(string(token)))''', '''\tmetadata := json.RawMessage(raw)\n\tif len(bytes.TrimSpace(raw)) == 0 {\n\t\tmetadata = json.RawMessage(`{}`)\n\t}\n\tpayload := map[string]any{"envelope": map[string]any{\n\t\t"schemaVersion": "alps.dev/host-observation/v1",\n\t\t"host":          *host,\n\t\t"event":         *event,\n\t\t"occurredAt":    time.Now().UTC().Format(time.RFC3339Nano),\n\t\t"metadata":      metadata,\n\t}}\n\ttoken, _ := os.ReadFile(filepath.Join(*workspace, "runtime", "access.token"))\n\treturn postJSON(endpoint+"/v1/host-observations", payload, strings.TrimSpace(string(token)), map[string]string{"X-ALPS-Actor-Type": "system", "X-ALPS-Channel": "hook"})''')
value = value.replace('endpoint+"/api/runs/"+*runID+"/export"', 'endpoint+"/v1/runs/"+*runID+"/export"')
old = '''func postJSON(url string, payload any, token string) error {\n\tbody, _ := json.Marshal(payload)\n\treq, _ := http.NewRequest(http.MethodPost, url, strings.NewReader(string(body)))\n\treq.Header.Set("Content-Type", "application/json")\n\tif token != "" {\n\t\treq.Header.Set("Authorization", "Bearer "+token)\n\t}\n\tresp, err := http.DefaultClient.Do(req)'''
new = '''func postJSON(url string, payload any, token string, extraHeaders ...map[string]string) error {\n\tbody, _ := json.Marshal(payload)\n\treq, _ := http.NewRequest(http.MethodPost, url, bytes.NewReader(body))\n\treq.Header.Set("Content-Type", "application/json")\n\treq.Header.Set("Idempotency-Key", fmt.Sprintf("cli:%d:%d", os.Getpid(), time.Now().UnixNano()))\n\treq.Header.Set("X-ALPS-Actor-Type", "system")\n\treq.Header.Set("X-ALPS-Actor-ID", "local-cli")\n\treq.Header.Set("X-ALPS-Channel", "internal")\n\tif len(extraHeaders) > 0 {\n\t\tfor name, value := range extraHeaders[0] {\n\t\t\treq.Header.Set(name, value)\n\t\t}\n\t}\n\tif token != "" {\n\t\treq.Header.Set("Authorization", "Bearer "+token)\n\t}\n\tresp, err := http.DefaultClient.Do(req)'''
if old not in value:
    raise SystemExit("missing postJSON pattern in cmd/alps/main.go")
main.write_text(value.replace(old, new))
replace(
    "web/src/lib/types.ts",
    '''export type Evidence = { artifactId?: string; eventId?: string; uri?: string; digest?: string; note?: string };''',
    '''export type Evidence = { kind: string; id: string; uri?: string; digest?: string; description?: string };''',
)
replace(
    "web/src/lib/components/DecisionDialog.svelte",
    '''<li>{item.note || item.artifactId || item.uri || item.digest}</li>''',
    '''<li>{item.description || item.id || item.uri || item.digest}</li>''',
)
replace(
    "web/src/lib/format.ts",
    '''export function number(value: unknown): string {\n  return typeof value === 'number' ? new Intl.NumberFormat().format(value) : value == null ? '—' : String(value);\n}''',
    '''export function number(value: unknown): string {\n  if (typeof value === 'number') return new Intl.NumberFormat().format(value);\n  if (value == null) return '—';\n  if (Array.isArray(value)) return `${value.length} item${value.length === 1 ? '' : 's'}`;\n  if (typeof value === 'object') {\n    const count = Object.keys(value as Record<string, unknown>).length;\n    return `${count} group${count === 1 ? '' : 's'}`;\n  }\n  return String(value);\n}''',
)
viewer = Path("web/src/lib/components/SkillViewer.svelte")
value = viewer.read_text()
old = '''  $: action = detail.data?.alpsState === 'adopted' ? 'Start Run' : detail.data?.alpsState === 'changed' ? 'Compare Changes' : detail.data?.validation === 'valid' ? 'Adopt Skill' : 'Review Validation';\n  function primary() { if (detail.data?.alpsState === 'adopted') start.mutate(); else if (detail.data?.validation === 'valid') adopt.mutate(); }'''
new = '''  $: assetLabel = detail.data?.kind === 'plugin' ? 'Plugin' : detail.data?.kind === 'process-model' ? 'Model' : 'Skill';\n  $: action = detail.data?.alpsState === 'adopted'\n    ? detail.data?.kind === 'skill' ? 'Start Run' : 'Adopted'\n    : detail.data?.alpsState === 'changed' ? 'Adopt New Revision'\n    : detail.data?.validation === 'valid' ? `Adopt ${assetLabel}` : 'Review Validation';\n  $: actionDisabled = adopt.isPending || start.isPending || (detail.data?.alpsState === 'adopted' && detail.data?.kind !== 'skill') || detail.data?.validation !== 'valid';\n  function primary() { if (detail.data?.alpsState === 'adopted' && detail.data?.kind === 'skill') start.mutate(); else if (detail.data?.validation === 'valid') adopt.mutate(); }'''
if old not in value:
    raise SystemExit("missing SkillViewer action pattern")
value = value.replace(old, new).replace('disabled={adopt.isPending || start.isPending}', 'disabled={actionDisabled}')
viewer.write_text(value)
package = json.loads(Path("web/package.json").read_text())
versions = {
    "@tanstack/svelte-query": "6.1.38", "@tanstack/svelte-virtual": "3.13.36", "bits-ui": "2.19.0",
    "d3-selection": "3.0.0", "d3-zoom": "3.0.0", "@playwright/test": "1.62.1",
    "@sveltejs/adapter-static": "3.0.10", "@sveltejs/kit": "2.70.3", "@sveltejs/vite-plugin-svelte": "7.3.0",
    "@tailwindcss/vite": "4.3.3", "@types/d3-selection": "3.0.11", "@types/d3-zoom": "3.0.8",
    "svelte": "5.56.10", "svelte-check": "4.7.6", "tailwindcss": "4.3.3", "typescript": "6.0.3",
    "vite": "8.2.2", "vitest": "4.1.11",
}
for section in ("dependencies", "devDependencies"):
    for name in package[section]:
        package[section][name] = versions[name]
Path("web/package.json").write_text(json.dumps(package, indent=2) + "\n")
